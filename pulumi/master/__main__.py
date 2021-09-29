import json

import pulumi
import pulumi_aws as aws

k8s_vpc = aws.ec2.Vpc(
    "k8sVpc",
    cidr_block="10.240.0.0/16",
    tags={
        "Name": "k8sVpc",
        "Owner": "hhk7734",
    },
)

k8s_subnet_a = aws.ec2.Subnet(
    "k8sSubnetA",
    vpc_id=k8s_vpc.id,
    cidr_block="10.240.1.0/24",
    tags={
        "Name": "k8sSubnetA",
        "Owner": "hhk7734",
    },
)

k8s_master_0_ni = aws.ec2.NetworkInterface(
    "k8sMaster0NI",
    subnet_id=k8s_subnet_a.id,
    private_ips=["10.240.1.11"],
    tags={
        "Name": "k8sMaster0NI",
        "Owner": "hhk7734",
    },
)

k8s_master_0 = aws.ec2.Instance(
    "k8sMaster0",
    ami="ami-090717c950a5c34d3",  # Ubuntu Server 18.04 LTS
    instance_type="t3.medium",
    credit_specification=aws.ec2.InstanceCreditSpecificationArgs(
        cpu_credits="unlimited",
    ),
    network_interfaces=[
        aws.ec2.InstanceNetworkInterfaceArgs(
            network_interface_id=k8s_master_0_ni.id,
            device_index=0,
        )
    ],
    tags={
        "Name": "k8sMaster0",
        "Owner": "hhk7734",
    },
)
