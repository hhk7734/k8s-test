from pathlib import Path

import pulumi
import pulumi_aws as aws

import network
from iam import policy, role

stack = pulumi.get_stack()

BASE_DIR = Path(__file__).parent.resolve()

stack = pulumi.get_stack()
config = pulumi.Config()

cluster = config.require("cluster-name")
common_tags = {
    "Stack": stack,
    f"kubernetes.io/cluster/{cluster}": "owned",  # or "shared"
    "Manager": config.require("manager"),
}

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
    role=role.master_node.name,
    tags=_tags,
)

_tags = {"Name": "k8s-worker-instance-profile"}
_tags.update(common_tags)
k8s_worker_instance_profile = aws.iam.InstanceProfile(
    _tags["Name"],
    role=role.worker_node.name,
    tags=_tags,
)

_tags = {"Name": "k8s-master-0"}
_tags.update(common_tags)
k8s_master_0 = aws.ec2.Instance(
    _tags["Name"],
    ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
    instance_type="t3.medium",
    associate_public_ip_address=True,
    subnet_id=network.subnet[0].id,
    iam_instance_profile=k8s_master_instance_profile.name,
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_type="gp2",
        volume_size=50,
    ),
    # kubernetes.io/cluster/hhk-cluster
    # Error syncing load balancer: failed to ensure load balancer:
    #   Multiple tagged security groups found for instance i-03d3679bc8bdf3374;
    #   ensure only the k8s security group is tagged;
    #   the tagged groups were sg-xxx sg-yyy
    vpc_security_group_ids=[
        network.common_sg.id,
        network.elb_sg.id,
    ],
    key_name=k8s_key_pair.key_name,
    tags=_tags,
)

k8s_workers = []
for i in range(1):
    _tags = {"Name": f"k8s-worker-{i}"}
    _tags.update(common_tags)
    k8s_workers.append(
        aws.ec2.Instance(
            _tags["Name"],
            ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
            instance_type="t3.large",
            associate_public_ip_address=True,
            subnet_id=network.subnet[0].id,
            iam_instance_profile=k8s_worker_instance_profile.name,
            root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
                volume_type="gp2",
                volume_size=30,
            ),
            # Ref: k8s-master-0
            vpc_security_group_ids=[
                network.common_sg.id,
                network.elb_sg.id,
            ],
            key_name=k8s_key_pair.key_name,
            tags=_tags,
        )
    )


pulumi.export("k8s-master-0-public-ip", k8s_master_0.public_ip)
pulumi.export("k8s-master-0-private-dns", k8s_master_0.private_dns)
for i, worker in enumerate(k8s_workers):
    pulumi.export(f"k8s-worker-{i}-public-ip", worker.public_ip)
    pulumi.export(f"k8s-worker-{i}-private-dns", worker.private_dns)
