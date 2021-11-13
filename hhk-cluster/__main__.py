from pathlib import Path

import pulumi
import pulumi_aws as aws

import iam
import network

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

_tags = {"Name": f"{cluster}-key-pair"}
_tags.update(common_tags)
k8s_key_pair = aws.ec2.KeyPair(
    _tags["Name"],
    key_name=_tags["Name"],
    public_key=public_key,
    tags=_tags,
)


masters = {}

for i in range(1):
    _tags = {"Name": f"{cluster}-master-node-{i}"}
    _tags.update(common_tags)
    masters[i] = aws.ec2.Instance(
        _tags["Name"],
        ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
        instance_type="t3.medium",
        associate_public_ip_address=True,
        subnet_id=network.subnet[0].id,
        iam_instance_profile=iam.master_node_profile.name,
        root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
            volume_type="gp2",
            volume_size=20,
        ),
        # kubernetes.io/cluster/kubernetes
        # Error syncing load balancer: failed to ensure load balancer:
        #   Multiple tagged security groups found for instance i-03d3679bc8bdf3374;
        #   ensure only the k8s security group is tagged;
        #   the tagged groups were sg-xxx sg-yyy
        vpc_security_group_ids=[
            network.common_sg.id,
            network.elb_sg.id,
            network.ssh_sg.id,
        ],
        key_name=k8s_key_pair.key_name,
        tags=_tags,
    )


# TODO: ASG

workers = {}

for i in range(2):
    _tags = {"Name": f"{cluster}-worker-node-{i}"}
    _tags.update(common_tags)
    workers[i] = aws.ec2.Instance(
        _tags["Name"],
        ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
        instance_type="t3.large",
        associate_public_ip_address=True,
        subnet_id=network.subnet[0].id,
        iam_instance_profile=iam.worker_node_profile.name,
        root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
            volume_type="gp2",
            volume_size=30,
        ),
        # Ref: k8s-master-0
        vpc_security_group_ids=[
            network.common_sg.id,
            network.elb_sg.id,
            network.ssh_sg.id,
        ],
        key_name=k8s_key_pair.key_name,
        tags=_tags,
    )

for i, master in masters.items():
    pulumi.export(f"{cluster}-master-{i}-public-ip", master.public_ip)
    pulumi.export(f"{cluster}-master-{i}-private-dns", master.private_dns)
for i, worker in workers.items():
    pulumi.export(f"{cluster}-worker-{i}-public-ip", worker.public_ip)
    pulumi.export(f"{cluster}-worker-{i}-private-dns", worker.private_dns)

# rds = {}

# _tags = {"Name": f"{cluster}-rds-0"}
# _tags.update(common_tags)
# rds[0] = aws.rds.Instance(
#     _tags["Name"],
#     engine="mysql",
#     engine_version="8.0.23",
#     identifier=_tags["Name"],
#     username="kubeflow",
#     password="kubeflow",
#     instance_class="db.m6g.large",
#     storage_type="gp2",
#     allocated_storage=20,
#     multi_az=False,
#     db_subnet_group_name=network.rds_subnet[0].name,
#     publicly_accessible=False,
#     vpc_security_group_ids=[network.common_sg.id],
#     tags=_tags,
# )

# s3 = {}

# _tags = {"Name": f"{cluster}-s3-0"}
# _tags.update(common_tags)
# s3[0] = aws.s3.Bucket(
#     _tags["Name"],
#     bucket="hitsai-kubeflow",
#     acl="private",
#     tags=_tags,
# )
