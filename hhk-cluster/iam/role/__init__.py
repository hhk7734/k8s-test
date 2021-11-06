from pathlib import Path

import pulumi
import pulumi_aws as aws

BASE_DIR = Path(__file__).parent.resolve()

stack = pulumi.get_stack()
config = pulumi.Config()

cluster = config.require("cluster-name")
common_tags = {
    "Stack": stack,
    f"kubernetes.io/cluster/{cluster}": "owned",  # or "shared"
    "Manager": config.require("manager"),
}

_tags = {"Name": f"{cluster}-master-node-role"}
_tags.update(common_tags)
master_node = aws.iam.Role(
    _tags["Name"],
    assume_role_policy=BASE_DIR.joinpath(
        "master-node.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)

_tags = {"Name": f"{cluster}-worker-node-role"}
_tags.update(common_tags)
worker_node = aws.iam.Role(
    _tags["Name"],
    assume_role_policy=BASE_DIR.joinpath(
        "worker-node.json",
    ).read_text(encoding="utf-8"),
    tags=_tags,
)
