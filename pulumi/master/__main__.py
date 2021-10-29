import json
from pathlib import Path

import pulumi
import pulumi_aws as aws

stack = pulumi.get_stack()

BASE_DIR = Path(__file__).parent.resolve()

# 10.234.0.0/16
# 10.234.0.0 네트워크 주소
# 10.234.0.1 VPC 라우터 주소
# 10.234.0.2 DNS 서버 주소
# 10.234.0.3 Reserved
# 10.234.255.255 Reserved
k8s_vpc = aws.ec2.Vpc(
    "k8s_vpc",
    cidr_block="10.234.0.0/16",
    tags={
        "Name": "k8s_vpc",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_internet_gateway = aws.ec2.InternetGateway(
    "k8s_internet_gateway",
    vpc_id=k8s_vpc.id,
    tags={
        "Name": "k8s_internet_gateway",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_route_table_0 = aws.ec2.RouteTable(
    "k8s_route_table_0",
    vpc_id=k8s_vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=k8s_internet_gateway.id,
        ),  # Public
    ],
    tags={
        "Name": "k8s_route_table_0",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

availability_zones = aws.get_availability_zones(state="available")

k8s_subnet_0 = aws.ec2.Subnet(
    "k8s_subnet_0",
    vpc_id=k8s_vpc.id,
    cidr_block="10.234.1.0/24",
    availability_zone=availability_zones.names[0],
    map_public_ip_on_launch=True,
    tags={
        "Name": "k8s_subnet_0",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_subnet_1 = aws.ec2.Subnet(
    "k8s_subnet_1",
    vpc_id=k8s_vpc.id,
    cidr_block="10.234.128.0/24",
    availability_zone=availability_zones.names[1],
    map_public_ip_on_launch=True,
    tags={
        "Name": "k8s_subnet_1",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_route_table_association_0 = aws.ec2.RouteTableAssociation(
    "k8s_route_table_association_0",
    subnet_id=k8s_subnet_0.id,
    route_table_id=k8s_route_table_0.id,
)

k8s_route_table_association_1 = aws.ec2.RouteTableAssociation(
    "k8s_route_table_association_1",
    subnet_id=k8s_subnet_1.id,
    route_table_id=k8s_route_table_0.id,
)

k8s_common_security_group = aws.ec2.SecurityGroup(
    "k8s_common_security_group",
    description="k8s Common Security Group",
    vpc_id=k8s_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=0,
            to_port=0,
            protocol="all",
            self=True,
        ),
    ],
    egress=[],
    tags={
        "Name": "k8s_common_security_group",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)


k8s_master_security_group = aws.ec2.SecurityGroup(
    "k8s_master_security_group",
    description="k8s Master Security Group",
    vpc_id=k8s_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            from_port=433,
            to_port=433,
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
    tags={
        "Name": "k8s_master_security_group",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_worker_security_group = aws.ec2.SecurityGroup(
    "k8s_worker_security_group",
    description="k8s Master Security Group",
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
    tags={
        "Name": "k8s_worker_security_group",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_master_iam_role = aws.iam.Role(
    "k8s_master_iam_role",
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
    tags={
        "Name": "k8s_master_iam_role",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_worker_iam_role = aws.iam.Role(
    "k8s_worker_iam_role",
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
    tags={
        "Name": "k8s_worker_iam_role",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_load_balancer = aws.lb.LoadBalancer(
    "k8s-load-balancer",
    load_balancer_type="network",
    internal=False,
    subnets=[
        k8s_subnet_0.id,
        k8s_subnet_1.id,
    ],
    tags={
        "Name": "k8s-load-balancer",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_lb_http_tg = aws.lb.TargetGroup(
    "k8s-lb-http-tg",
    port=80,
    protocol="TCP",
    vpc_id=k8s_vpc.id,
    tags={
        "Name": "k8s-lb-http-tg",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_lb_http_listener = aws.lb.Listener(
    "k8s-lb-http-listener",
    load_balancer_arn=k8s_load_balancer.arn,
    port=80,
    protocol="TCP",
    default_actions=[
        aws.lb.ListenerDefaultActionArgs(
            type="forward",
            target_group_arn=k8s_lb_http_tg.arn,
        ),
    ],
    tags={
        "Name": "k8s-lb-http-listener",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_lb_https_tg = aws.lb.TargetGroup(
    "k8s-lb-https-tg",
    port=433,
    protocol="TCP",
    vpc_id=k8s_vpc.id,
    tags={
        "Name": "k8s-lb-https-tg",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_lb_https_listener = aws.lb.Listener(
    "k8s-lb-https-listener",
    load_balancer_arn=k8s_load_balancer.arn,
    port=433,
    protocol="TCP",
    default_actions=[
        aws.lb.ListenerDefaultActionArgs(
            type="forward",
            target_group_arn=k8s_lb_https_tg.arn,
        ),
    ],
    tags={
        "Name": "k8s-lb-https-listener",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

with BASE_DIR.joinpath("iam", "policy", "master.json").open() as fd:
    master_policy = fd.read()

k8s_master_iam_policy = aws.iam.RolePolicy(
    "k8s_master_iam_policy",
    role=k8s_master_iam_role.id,
    policy=master_policy,
)

with BASE_DIR.joinpath("iam", "policy", "worker.json").open() as fd:
    worker_policy = fd.read()

k8s_worker_iam_policy = aws.iam.RolePolicy(
    "k8s_worker_iam_policy",
    role=k8s_worker_iam_role.id,
    policy=worker_policy,
)

with Path.home().joinpath(".ssh", "authorized_keys").open() as fd:
    public_key = fd.readline().strip("\n")

k8s_key_pair = aws.ec2.KeyPair(
    "k8s_key_pair",
    key_name="k8s_key_pair",
    public_key=public_key,
    tags={
        "Name": "k8s_key_pair",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_master_instance_profile = aws.iam.InstanceProfile(
    "k8s_master_instance_profile",
    role=k8s_master_iam_role.name,
    tags={
        "Name": "k8s_master_instance_profile",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_worker_instance_profile = aws.iam.InstanceProfile(
    "k8s_worker_instance_profile",
    role=k8s_worker_iam_role.name,
    tags={
        "Name": "k8s_worker_instance_profile",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_master_0 = aws.ec2.Instance(
    "k8s_master_0",
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
    tags={
        "Name": "k8s_master_0",
        "Stack": stack,
        "Owner": "hhk7734",
    },
)

k8s_worker = []
for i in range(2):
    k8s_worker.append(
        aws.ec2.Instance(
            f"k8s_worker_{i}",
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
            tags={
                "Name": f"k8s_worker_{i}",
                "Stack": stack,
                "Owner": "hhk7734",
            },
        )
    )


pulumi.export("k8s_master_0_public_ip", k8s_master_0.public_ip)
pulumi.export("k8s_master_0_private_ip", k8s_master_0.private_ip)
for i in range(2):
    pulumi.export(f"k8s_worker_{i}_public_ip", k8s_worker[i].public_ip)
    pulumi.export(f"k8s_worker_{i}_private_ip", k8s_worker[i].private_ip)
