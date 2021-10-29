import json
from pathlib import Path

import pulumi
import pulumi_aws as aws

stack = pulumi.get_stack()

BASE_DIR = Path(__file__).parent.resolve()

common_tags = {
    "Stack": stack,
    "kubernetes.io/cluster/hhk-cluster": "owned",  # or "shared"
    "Owner": "hhk7734",
}

# 10.234.0.0/16
# 10.234.0.0 네트워크 주소
# 10.234.0.1 VPC 라우터 주소
# 10.234.0.2 DNS 서버 주소
# 10.234.0.3 Reserved
# 10.234.255.255 Reserved
_tags = {"Name": "k8s-vpc"}
_tags.update(common_tags)
k8s_vpc = aws.ec2.Vpc(
    _tags["Name"],
    cidr_block="10.234.0.0/16",
    tags=_tags,
)

_tags = {"Name": "k8s-igw"}
_tags.update(common_tags)
k8s_internet_gateway = aws.ec2.InternetGateway(
    _tags["Name"],
    vpc_id=k8s_vpc.id,
    tags=_tags,
)


_tags = {"Name": "k8s-route-table-0"}
_tags.update(common_tags)
k8s_route_table_0 = aws.ec2.RouteTable(
    _tags["Name"],
    vpc_id=k8s_vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=k8s_internet_gateway.id,
        ),  # Public
    ],
    tags=_tags,
)

availability_zones = aws.get_availability_zones(state="available")

_tags = {
    "Name": "k8s-subnet-0",
    "kubernetes.io/role/elb": "1",
}
_tags.update(common_tags)
k8s_subnet_0 = aws.ec2.Subnet(
    _tags["Name"],
    vpc_id=k8s_vpc.id,
    cidr_block="10.234.1.0/24",
    availability_zone=availability_zones.names[0],
    map_public_ip_on_launch=True,
    tags=_tags,
)


_tags = {"Name": "k8s-route-table-association-0"}
_tags.update(common_tags)
k8s_route_table_association_0 = aws.ec2.RouteTableAssociation(
    _tags["Name"],
    subnet_id=k8s_subnet_0.id,
    route_table_id=k8s_route_table_0.id,
)

_tags = {"Name": "k8s-common-sg"}
_tags.update(common_tags)
k8s_common_security_group = aws.ec2.SecurityGroup(
    _tags["Name"],
    vpc_id=k8s_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=0,
            to_port=0,
            protocol="all",
            self=True,
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="all",
            self=True,
        ),
    ],
    tags=_tags,
)


_tags = {"Name": "k8s-master-sg"}
_tags.update(common_tags)
k8s_master_security_group = aws.ec2.SecurityGroup(
    _tags["Name"],
    vpc_id=k8s_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            from_port=30000,
            to_port=32767,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags=_tags,
)

_tags = {"Name": "k8s-worker-sg"}
_tags.update(common_tags)
k8s_worker_security_group = aws.ec2.SecurityGroup(
    _tags["Name"],
    vpc_id=k8s_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            from_port=30000,
            to_port=32767,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags=_tags,
)

_tags = {"Name": "k8s-master-iam-role"}
_tags.update(common_tags)
k8s_master_iam_role = aws.iam.Role(
    _tags["Name"],
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }
    ),
    tags=_tags,
)

_tags = {"Name": "k8s-worker-iam-role"}
_tags.update(common_tags)
k8s_worker_iam_role = aws.iam.Role(
    _tags["Name"],
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }
    ),
    tags=_tags,
)

with BASE_DIR.joinpath("iam", "policy", "master.json").open() as fd:
    master_policy = fd.read()

_tags = {"Name": "k8s-master-iam-policy"}
_tags.update(common_tags)
k8s_master_iam_policy = aws.iam.RolePolicy(
    _tags["Name"],
    role=k8s_master_iam_role.id,
    policy=master_policy,
)

with BASE_DIR.joinpath("iam", "policy", "worker.json").open() as fd:
    worker_policy = fd.read()

_tags = {"Name": "k8s-worker-iam-policy"}
_tags.update(common_tags)
k8s_worker_iam_policy = aws.iam.RolePolicy(
    _tags["Name"],
    role=k8s_worker_iam_role.id,
    policy=worker_policy,
)

with Path.home().joinpath(".ssh", "authorized_keys").open() as fd:
    public_key = fd.readline().strip("\n")

_tags = {"Name": "k8s-key-pair"}
_tags.update(common_tags)
k8s_key_pair = aws.ec2.KeyPair(
    _tags["Name"],
    key_name="k8s-key-pair",
    public_key=public_key,
    tags=_tags,
)

_tags = {"Name": "k8s-master-instance-profile"}
_tags.update(common_tags)
k8s_master_instance_profile = aws.iam.InstanceProfile(
    _tags["Name"],
    role=k8s_master_iam_role.name,
    tags=_tags,
)

_tags = {"Name": "k8s-worker-instance-profile"}
_tags.update(common_tags)
k8s_worker_instance_profile = aws.iam.InstanceProfile(
    _tags["Name"],
    role=k8s_worker_iam_role.name,
    tags=_tags,
)

_tags = {"Name": "k8s-master-0"}
_tags.update(common_tags)
k8s_master_0 = aws.ec2.Instance(
    _tags["Name"],
    ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
    instance_type="t3.medium",
    associate_public_ip_address=True,
    subnet_id=k8s_subnet_0.id,
    iam_instance_profile=k8s_master_instance_profile.name,
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_type="gp2",
        volume_size=50,
    ),
    vpc_security_group_ids=[
        k8s_common_security_group.id,
        k8s_master_security_group.id,
    ],
    key_name=k8s_key_pair.key_name,
    tags=_tags,
)

k8s_worker = []
for i in range(2):
    k8s_worker.append(
        aws.ec2.Instance(
            f"k8s-worker-{i}",
            ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
            instance_type="t3.large",
            associate_public_ip_address=True,
            subnet_id=k8s_subnet_0.id,
            iam_instance_profile=k8s_worker_instance_profile.name,
            root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
                volume_type="gp2",
                volume_size=30,
            ),
            vpc_security_group_ids=[
                k8s_common_security_group.id,
                k8s_worker_security_group.id,
            ],
            key_name=k8s_key_pair.key_name,
            tags=_tags,
        )
    )


pulumi.export("k8s-master-0-public-ip", k8s_master_0.public_ip)
pulumi.export("k8s-master-0-private-dns", k8s_master_0.private_dns)
for i in range(2):
    pulumi.export(f"k8s-worker-{i}-public-ip", k8s_worker[i].public_ip)
    pulumi.export(f"k8s-worker-{i}-private-dns", k8s_worker[i].private_dns)
