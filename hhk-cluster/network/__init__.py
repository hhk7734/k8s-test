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

# class 별 사설 IP 주소
# 10.0.0.0/8      10.0.0.0    ~ 10.255.255.255   A 클래스 1 개
# 172.16.0.0/12   172.16.0.0  ~ 172.31.255.255   B 클래스 16 개
# 192.168.0.0/16  192.168.0.0 ~ 192.168.255.255  C 클래스 256 개

# 10.234.0.0/16
# 10.234.0.0 네트워크 주소
# 10.234.0.1 VPC 라우터 주소
# 10.234.0.2 DNS 서버 주소
# 10.234.0.3 Reserved
# 10.234.255.255 Reserved

_tags = {"Name": f"{cluster}-vpc"}
_tags.update(common_tags)
vpc = aws.ec2.Vpc(
    _tags["Name"],
    cidr_block="10.234.0.0/16",
    tags=_tags,
)

_tags = {"Name": f"{cluster}-igw"}
_tags.update(common_tags)
igw = aws.ec2.InternetGateway(
    _tags["Name"],
    vpc_id=vpc.id,
    tags=_tags,
    opts=pulumi.ResourceOptions(parent=vpc),
)

rtb = {}

_tags = {"Name": f"{cluster}-rtb-0"}
_tags.update(common_tags)
rtb[0] = aws.ec2.RouteTable(
    _tags["Name"],
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        ),  # Public
    ],
    tags=_tags,
    opts=pulumi.ResourceOptions(parent=vpc),
)


AZs = aws.get_availability_zones(state="available")

subnet = {}

_tags = {
    "Name": f"{cluster}-subnet-0",
    "kubernetes.io/role/elb": "1",  # 로드밸런서가 연결될 서브넷
}
_tags.update(common_tags)
subnet[0] = aws.ec2.Subnet(
    _tags["Name"],
    vpc_id=vpc.id,
    cidr_block="10.234.1.0/24",
    availability_zone=AZs.names[0],
    map_public_ip_on_launch=True,
    tags=_tags,
    opts=pulumi.ResourceOptions(parent=vpc),
)

rtb_assoc = {}

_tags = {"Name": f"{cluster}-rtb-assoc-0"}
rtb_assoc[0] = aws.ec2.RouteTableAssociation(
    _tags["Name"],
    subnet_id=subnet[0].id,
    route_table_id=rtb[0].id,
    opts=pulumi.ResourceOptions(parent=rtb[0]),
)

# 이 scurity group은 cluster load balancer를 위한 것이기 때문에 ingress가
# 자동으로 수정될 수 있습니다.
_tags = {"Name": f"{cluster}-elb-sg"}
_tags.update(common_tags)
elb_sg = aws.ec2.SecurityGroup(
    _tags["Name"],
    vpc_id=vpc.id,
    tags=_tags,
    opts=pulumi.ResourceOptions(ignore_changes=["ingress"], parent=vpc),
)

_tags = {"Name": f"{cluster}-common-sg"}
_tags.update(common_tags)
common_sg = aws.ec2.SecurityGroup(
    _tags["Name"],
    vpc_id=vpc.id,
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
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags=_tags,
    opts=pulumi.ResourceOptions(parent=vpc),
)
