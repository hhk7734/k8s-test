import json

import pulumi
import pulumi_aws as aws

# 10.234.0.0/16
# 10.234.0.0 네트워크 주소
# 10.234.0.1 VPC 라우터 주소
# 10.234.0.2 DNS 서버 주소
# 10.234.0.3 Reserved
# 10.234.255.255 Reserved
k8s_vpc = aws.ec2.Vpc(
    "k8sVpc",
    cidr_block="10.234.0.0/16",
    tags={
        "Name": "k8sVpc",
        "Owner": "hhk7734",
    },
)

k8s_subnet_a = aws.ec2.Subnet(
    "k8sSubnetA",
    vpc_id=k8s_vpc.id,
    cidr_block="10.234.1.0/24",
    tags={
        "Name": "k8sSubnetA",
        "Owner": "hhk7734",
    },
)

k8s_igw = aws.ec2.InternetGateway(
    "k8sIGW",
    vpc_id=k8s_vpc.id,
    tags={
        "Name": "k8sIGW",
        "Owner": "hhk7734",
    },
)

k8s_master_0 = aws.ec2.Instance(
    "k8sMaster0",
    ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
    instance_type="t3.medium",
    associate_public_ip_address=True,
    subnet_id=k8s_subnet_a.id,
    credit_specification=aws.ec2.InstanceCreditSpecificationArgs(
        cpu_credits="unlimited",
    ),
    tags={
        "Name": "k8sMaster0",
        "Owner": "hhk7734",
    },
)
