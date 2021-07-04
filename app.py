#!/usr/bin/env python3
import os
from aws_cdk import core as cdk

from stacks.back_end.vpc_stack import VpcStack
from stacks.back_end.eks_cluster_stacks.eks_cluster_stack import EksClusterStack
from stacks.back_end.eks_cluster_stacks.eks_ssm_daemonset_stack.eks_ssm_daemonset_stack import EksSsmDaemonSetStack
from stacks.back_end.efs_stack import EfsStack


app = cdk.App()

# VPC Stack for hosting Secure workloads & Other resources
vpc_stack = VpcStack(
    app,
    # f"{app.node.try_get_context('project')}-vpc-stack",
    "eks-cluster-vpc-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: Custom Multi-AZ VPC"
)


# EKS Cluster to process event processor
eks_cluster_stack = EksClusterStack(
    app,
    f"eks-cluster-stack",
    stack_log_level="INFO",
    vpc=vpc_stack.vpc,
    description="Miztiik Automation: EKS Cluster to process event processor"
)

# Bootstrap EKS Nodes with SSM Agents
ssm_agent_installer_daemonset = EksSsmDaemonSetStack(
    app,
    f"ssm-agent-installer-daemonset-stack",
    stack_log_level="INFO",
    eks_cluster=eks_cluster_stack.eks_cluster_1,
    description="Miztiik Automation: Bootstrap EKS Nodes with SSM Agents"
)

# Create EFS
efs_stack = EfsStack(
    app,
    "efs-stack",
    stack_log_level="INFO",
    vpc=vpc_stack.vpc,
    description="Miztiik Automation: Deploy AWS Elastic File System Stack"
)

# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            cdk.Tags.of(app).add(
                k, v, apply_to_launched_instances=True, priority=300)

app.synth()
