import json
from pathlib import Path

import pulumi
import pulumi_aws as aws

stack = pulumi.get_stack()

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

k8s_route_table_association_0 = aws.ec2.RouteTableAssociation(
    "k8s_route_table_association_0",
    subnet_id=k8s_subnet_0.id,
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

k8s_master_iam_policy = aws.iam.RolePolicy(
    "k8s_master_iam_policy",
    role=k8s_master_iam_role.id,
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:DescribeLaunchConfigurations",
                        "autoscaling:DescribeTags",
                        "ec2:DescribeInstances",
                        "ec2:DescribeRegions",
                        "ec2:DescribeRouteTables",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeVolumes",
                        "ec2:CreateSecurityGroup",
                        "ec2:CreateTags",
                        "ec2:CreateVolume",
                        "ec2:ModifyInstanceAttribute",
                        "ec2:ModifyVolume",
                        "ec2:AttachVolume",
                        "ec2:AuthorizeSecurityGroupIngress",
                        "ec2:CreateRoute",
                        "ec2:DeleteRoute",
                        "ec2:DeleteSecurityGroup",
                        "ec2:DeleteVolume",
                        "ec2:DetachVolume",
                        "ec2:RevokeSecurityGroupIngress",
                        "ec2:DescribeVpcs",
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:AttachLoadBalancerToSubnets",
                        "elasticloadbalancing:ApplySecurityGroupsToLoadBalancer",
                        "elasticloadbalancing:CreateLoadBalancer",
                        "elasticloadbalancing:CreateLoadBalancerPolicy",
                        "elasticloadbalancing:CreateLoadBalancerListeners",
                        "elasticloadbalancing:ConfigureHealthCheck",
                        "elasticloadbalancing:DeleteLoadBalancer",
                        "elasticloadbalancing:DeleteLoadBalancerListeners",
                        "elasticloadbalancing:DescribeLoadBalancers",
                        "elasticloadbalancing:DescribeLoadBalancerAttributes",
                        "elasticloadbalancing:DetachLoadBalancerFromSubnets",
                        "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                        "elasticloadbalancing:ModifyLoadBalancerAttributes",
                        "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
                        "elasticloadbalancing:SetLoadBalancerPoliciesForBackendServer",
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:CreateListener",
                        "elasticloadbalancing:CreateTargetGroup",
                        "elasticloadbalancing:DeleteListener",
                        "elasticloadbalancing:DeleteTargetGroup",
                        "elasticloadbalancing:DescribeListeners",
                        "elasticloadbalancing:DescribeLoadBalancerPolicies",
                        "elasticloadbalancing:DescribeTargetGroups",
                        "elasticloadbalancing:DescribeTargetHealth",
                        "elasticloadbalancing:ModifyListener",
                        "elasticloadbalancing:ModifyTargetGroup",
                        "elasticloadbalancing:RegisterTargets",
                        "elasticloadbalancing:DeregisterTargets",
                        "elasticloadbalancing:SetLoadBalancerPoliciesOfListener",
                        "iam:CreateServiceLinkedRole",
                        "kms:DescribeKey",
                    ],
                    "Resource": ["*"],
                }
            ],
        }
    ),
)

k8s_worker_iam_policy = aws.iam.RolePolicy(
    "k8s_worker_iam_policy",
    role=k8s_worker_iam_role.id,
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:DescribeInstances",
                        "ec2:DescribeRegions",
                        "ecr:GetAuthorizationToken",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:GetRepositoryPolicy",
                        "ecr:DescribeRepositories",
                        "ecr:ListImages",
                        "ecr:BatchGetImage",
                    ],
                    "Resource": ["*"],
                }
            ],
        }
    ),
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
