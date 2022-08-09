from os import cpu_count

from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as _iam
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct
from aws_cdk import aws_medialive as medialive


class EcsClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        docker_dir = self.node.try_get_context("envs")['prod']['docker_dir']

        # cfn_public_repository = _ecr.Repository(self, "MyCfnPublicRepository",
        #                         repository_name="mm_ecr_repo",
        #                         )
        

        vpc= ec2.Vpc.from_lookup(self, "vpc", 
                                vpc_id="vpc-04fac8c36ede5681b"
                                )     # default is all AZs in region

        cluster = ecs.Cluster(self, "FargateCPCluster",
                                vpc=vpc,
                                enable_fargate_capacity_providers=True,
                                )
        
        asset = DockerImageAsset(self,
                                 "MyBuildImage",
                                 directory=f"{docker_dir}",
                                )

        task_definition = ecs.FargateTaskDefinition(self, "TaskDef")
        task_definition.add_to_execution_role_policy(_iam.PolicyStatement(
                                resources=["*"],
                                actions= [
                                          "ecr:GetAuthorizationToken",
                                          "ecr:BatchCheckLayerAvailability",
                                          "ecr:GetDownloadUrlForLayer","ecr:BatchGetImage",
                                          "logs:CreateLogStream","logs:PutLogEvents"
                                        ],
                                ))

        task_definition.add_container("web",
                                image=ecs.ContainerImage.from_registry(asset.repository),
                                )

        ecs.FargateService(self, "FargateService",
                                cluster=cluster,
                                task_definition=task_definition,
                                capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                                    capacity_provider="FARGATE_SPOT",
                                    weight=2
                                ), ecs.CapacityProviderStrategy(
                                    capacity_provider="FARGATE",
                                    weight=1
                                )]
                                )