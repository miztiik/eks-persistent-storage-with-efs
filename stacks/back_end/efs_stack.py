
from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_efs as _efs
from stacks.miztiik_global_args import GlobalArgs

class EfsStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        stack_log_level,
        vpc,
        efs_mnt_path: str = "/efs",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Security Group to connect to EFS
        self.efs_sg = _ec2.SecurityGroup(
            self,
            id="efsSecurityGroup",
            vpc=vpc,
            security_group_name=f"efs-sg",
            description="Security Group to connect to EFS from the VPC"
        )

        self.efs_sg.add_ingress_rule(
            peer=_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=_ec2.Port.tcp(2049),
            description="Allow EC2 instances within the same VPC to connect to EFS"
        )

        # Let us create the EFS Filesystem
        self.efs_share = _efs.FileSystem(
            self,
            "elasticFileSystem",
            file_system_name=f"high-performance-storage",
            vpc=vpc,
            security_group=self.efs_sg,
            vpc_subnets=_ec2.SubnetSelection(subnet_type=_ec2.SubnetType.PUBLIC),
            encrypted=False,
            lifecycle_policy=_efs.LifecyclePolicy.AFTER_7_DAYS,
            performance_mode=_efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=_efs.ThroughputMode.BURSTING,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # create efs acl
        efs_acl = _efs.Acl(
            owner_gid="1000",
            owner_uid="1000",
            permissions="0777"
        )

        # create efs posix user
        efs_user = _efs.PosixUser(
            gid="1000",
            uid="1000"
        )

        # create efs access point
        self.efs_ap_01 = _efs.AccessPoint(
            self,
            "efsAccessPoint",
            path=f"{efs_mnt_path}",
            file_system=self.efs_share,
            posix_user=efs_user,
            create_acl=efs_acl
        )

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = cdk.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = cdk.CfnOutput(
            self,
            "EFSFileSystemId",
            value=f"{self.efs_share.file_system_id}",
            description="The ID of the file system, assigned by Amazon EFS"
        )

        output_2 = cdk.CfnOutput(
            self,
            "EFSAccessPointId",
            value=f"{self.efs_ap_01.access_point_id}",
            description="The The ID of the Access Point"
        )

        output_3 = cdk.CfnOutput(
            self,
            "MountEfs",
            value=f"sudo mount -t efs -o tls {self.efs_share.file_system_id}:/ /mnt/efs ",
            description="Use this command to mount efs using efs helper utility at location /mnt/efs"
        )
