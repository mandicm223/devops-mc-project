from os import cpu_count
from tracemalloc import take_snapshot

from aws_cdk import Duration
from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as _patterns
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_elasticloadbalancingv2 as _elb
import aws_cdk
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct


class EcsClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        docker_image = self.node.try_get_context("envs")['prod']['docker_dir']

        # cfn_public_repository = _ecr.Repository(self, "MyCfnPublicRepository",
        #                         repository_name="mm_ecr_repo",
        #                         )
        

        # vpc= ec2.Vpc.from_lookup(self, "vpc", 
        #                         vpc_id="vpc-04fac8c36ede5681b"
        #                         )     # default is all AZs in region
        prod_configs = self.node.try_get_context("envs")['prod']
        vpc_configs = self.node.try_get_context("envs")['prod']['vpc_configs']

        customVPC = ec2.Vpc(self,"customVPC",
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
                                vpc=customVPC,
                                enable_fargate_capacity_providers=True,
                                )

        task_definition = ecs.FargateTaskDefinition(self, "TaskDef",
                                memory_limit_mib=512,
                                cpu=256
                                )

        task_definition.add_to_execution_role_policy(_iam.PolicyStatement(
                                resources=["*"],
                                actions= [
                                          "ecr:GetAuthorizationToken",
                                          "ecr:BatchCheckLayerAvailability",
                                          "ecr:GetDownloadUrlForLayer","ecr:BatchGetImage",
                                          "logs:CreateLogStream","logs:PutLogEvents"
                                        ],
                                ))

        container = task_definition.add_container("swagger",
                                image=ecs.ContainerImage.from_registry("446835144354.dkr.ecr.eu-west-1.amazonaws.com/markomandicecrrepo"),
                                logging=ecs.AwsLogDriver(
                                    stream_prefix="mm-ecr"
                                )
                                )

        port_mapping = ecs.PortMapping(container_port=8080, host_port=80)
        container.add_port_mappings(port_mapping)

        ecs_fargate_service = ecs.FargateService(self, "FargateService",
                                cluster=cluster,
                                task_definition=task_definition,
                                assign_public_ip=True,
                                capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                                    capacity_provider="FARGATE_SPOT",
                                    weight=2
                                ), ecs.CapacityProviderStrategy(
                                    capacity_provider="FARGATE",
                                    weight=1
                                )]
                                )
        
        load_balancer = _elb.ApplicationLoadBalancer(self, "MMelasticNetworkLB",
                                vpc=customVPC,
                                internet_facing=True,
                                )

        listener = load_balancer.add_listener("mmListenerRule",
                                port=80,
                            )
        
        security_group_fargate = ec2.SecurityGroup("self", "mm-ecs-security-group",
                            vpc=customVPC,
                            allow_all_outbound=True)
        
        security_group_fargate.add_ingress_rule(ec2.Peer.ipv4('0.0.0.0./0'), ec2.Port.tcp(80))
        # security_group_lb.add_ingress_rule(ec2.Peer.ipv4('0.0.0.0./0'), ec2.Port.tcp(8080))

        listener.add_targets(self, "fargate_target_group",
                            port=80,
                            targets=[ecs_fargate_service],
                            deregistration_delay=aws_cdk.Duration(300)
                            )