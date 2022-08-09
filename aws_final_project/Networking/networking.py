from unicodedata import name

from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_codebuild as _codebuild
from aws_cdk import aws_codecommit as _codecommit
from aws_cdk import aws_codepipeline as _codepipeline
from aws_cdk import aws_codepipeline_actions as _actions
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct
from aws_cdk import aws_ssm as _ssm


class NetworkingtStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # docker_image = self.node.try_get_context("envs")['prod']['docker_dir']

        # repo = _codecommit.Repository(self,
        #                               "markomandicrepo",
        #                               repository_name="markomandic-repo",
        #                               description="markanov repo najjaci na svetu"
        #                             )
        prod_configs = self.node.try_get_context("envs")['prod']
        vpc_configs = self.node.try_get_context("envs")['prod']['vpc_configs']
        environment = self.node.try_get_context("envs")['prod']['env']
        first_name_last_name = self.node.try_get_context("envs")['prod']['first_last_name']

        custom_vpc = ec2.Vpc(self,
                            "custom_vpc",
                            max_azs=3,
                            nat_gateways=0,
                            # vpc_name=f"{environment}-vpc-{first_name_last_name}-custom_vpc",
                            # vpc_name=f"{environment}-{first_name_last_name}",
                            cidr=vpc_configs['vpc_cidr'],
                            subnet_configuration=[
                                ec2.SubnetConfiguration(
                                    name="MMPublicSubnet",
                                    subnet_type=ec2.SubnetType.PUBLIC,
                                    cidr_mask=vpc_configs['cidr_mask'] 
                                    ),
                                ec2.SubnetConfiguration(
                                    name="MMPrivateSubnet",
                                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                    cidr_mask=vpc_configs['cidr_mask']  
                                    )
                                ],
                            )

        vpcid = _ssm.StringParameter(self,
                                     'vpc_id',
                                     parameter_name= '/VpcProvider/markomandic/vpcid',
                                     string_value= custom_vpc.vpc_id
        )