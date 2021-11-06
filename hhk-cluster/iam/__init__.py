from pathlib import Path

import pulumi
import pulumi_aws as aws

from . import policy, role

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

_tags = {"Name": f"{cluster}-master-node-role-policy"}
aws.iam.RolePolicyAttachment(
    _tags["Name"],
    policy_arn=policy.master_node.arn,
    role=role.master_node.name,
    opts=pulumi.ResourceOptions(parent=role.master_node),
)

_tags = {"Name": f"{cluster}-master-node-profile"}
_tags.update(common_tags)
master_node_profile = aws.iam.InstanceProfile(
    _tags["Name"],
    role=role.master_node.name,
    tags=_tags,
)

_tags = {"Name": f"{cluster}-worker-node-role-policy"}
aws.iam.RolePolicyAttachment(
    _tags["Name"],
    policy_arn=policy.worker_node.arn,
    role=role.worker_node.name,
    opts=pulumi.ResourceOptions(parent=role.worker_node),
)

_tags = {"Name": f"{cluster}-worker-node-profile"}
_tags.update(common_tags)
worker_node_profile = aws.iam.InstanceProfile(
    _tags["Name"],
    role=role.worker_node.name,
    tags=_tags,
)
