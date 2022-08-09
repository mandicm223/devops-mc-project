from os import cpu_count

from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as _patterns
from aws_cdk import aws_iam as _iam
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct


class EcsClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        docker_dir = self.node.try_get_context("envs")['prod']['docker_dir']

        # cfn_public_repository = _ecr.Repository(self, "MyCfnPublicRepository",
        #                         repository_name="mm_ecr_repo",
        #                         )
        

        # vpc= ec2.Vpc.from_lookup(self, "vpc", 
        #                         vpc_id="vpc-04fac8c36ede5681b"
        #                         )     # default is all AZs in region
        prod_configs = self.node.try_get_context("envs")['prod']
        vpc_configs = self.node.try_get_context("envs")['prod']['vpc_configs']

        customVPC = ec2.Vpc(
            self,
            "customVPC",
            max_azs=3,
            nat_gateways=None,
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

        cluster = ecs.Cluster(self, "FargateCPCluster",
                                enable_fargate_capacity_providers=True,
                                )
        
        asset = DockerImageAsset(self,
                                 "MyBuildImage",
                                 directory=f"{docker_dir}",
                                )

        # task_definition = ecs.FargateTaskDefinition(self, "TaskDef")
        # task_definition.add_to_execution_role_policy(_iam.PolicyStatement(
        #                         resources=["*"],
        #                         actions= [
        #                                   "ecr:GetAuthorizationToken",
        #                                   "ecr:BatchCheckLayerAvailability",
        #                                   "ecr:GetDownloadUrlForLayer","ecr:BatchGetImage",
        #                                   "logs:CreateLogStream","logs:PutLogEvents"
        #                                 ],
        #                         ))

        # task_definition.add_container("web",
        #                         image=ecs.ContainerImage.from_registry(asset.repository),
        #                         )

        # ecs.FargateService(self, "FargateService",
        #                         cluster=cluster,
        #                         task_definition=task_definition,
        #                         capacity_provider_strategies=[ecs.CapacityProviderStrategy(
        #                             capacity_provider="FARGATE_SPOT",
        #                             weight=2
        #                         ), ecs.CapacityProviderStrategy(
        #                             capacity_provider="FARGATE",
        #                             weight=1
        #                         )]
        #                         )
        svc = _patterns.ApplicationLoadBalancedFargateService(self,
                                                               cluster=cluster,
                                                               memory_limit_mi_b=1024,
                                                               desired_count=1,
                                                               cpu=512,
                                                               task_image_options=_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                                   image=ecs.ContainerImage.from_registry(asset.repository),
                                                                   cluster=cluster,
                                                                   cpu=256,
                                                                   memory_limit_mi_b=512,
                                                                   
                                                               ),
                                                               task_subnets=ec2.SubnetSelection(
                                                                   subnets=[ customVPC.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)]
                                                               ),
                                                               public_load_balancer=True,
                                                               capacity_provider_strategies=[
                                                                   ecs.CapacityProviderStrategy(capacity_provider='FARGATE_SPOT', weight=2),
                                                                    ecs.CapacityProviderStrategy(capacity_provider='FARGATE', weight=1),
                                                                   
                                                               ]
        )