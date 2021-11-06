from pathlib import Path

import pulumi
import pulumi_aws as aws

BASE_DIR = Path(__file__).parent.resolve()

stack = pulumi.get_stack()
config = pulumi.Config()

common_tags = {
    "Stack": stack,
    f"kubernetes.io/cluster/{config.require('cluster-name')}": "owned",  # or "shared"
    "Manager": config.require("manager"),
}

_tags = {"Name": "master-node-policy"}
_tags.update(common_tags)
master_node = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "master-node.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)

_tags = {"Name": "worker-node-policy"}
_tags.update(common_tags)
worker_node = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "worker-node.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)

_tags = {"Name": "cluster-autoscaler-policy"}
_tags.update(common_tags)
cluster_autoscaler = aws.iam.Policy(
    _tags["Name"],
    policy=BASE_DIR.joinpath(
        "cluster-autoscaler.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)
