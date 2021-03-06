from pathlib import Path

import pulumi
import pulumi_aws as aws

from .. import role

BASE_DIR = Path(__file__).parent.resolve()

stack = pulumi.get_stack()
config = pulumi.Config()

cluster = config.require("cluster-name")
common_tags = {
    "Stack": stack,
    f"kubernetes.io/cluster/{cluster}": "owned",  # or "shared"
    "Manager": config.require("manager"),
}

_tags = {"Name": f"{cluster}-master-node-policy"}
_tags.update(common_tags)
master_node = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "master-node.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
    opts=pulumi.ResourceOptions(parent=role.master_node),
)

_tags = {"Name": f"{cluster}-worker-node-policy"}
_tags.update(common_tags)
worker_node = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "worker-node.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
    opts=pulumi.ResourceOptions(parent=role.worker_node),
)

_tags = {"Name": f"{cluster}-autoscaler-policy"}
_tags.update(common_tags)
cluster_autoscaler = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "cluster-autoscaler.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)

_tags = {"Name": f"{cluster}-ebs-csi-driver-policy"}
_tags.update(common_tags)
cluster_autoscaler = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "ebs-csi-driver.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)
