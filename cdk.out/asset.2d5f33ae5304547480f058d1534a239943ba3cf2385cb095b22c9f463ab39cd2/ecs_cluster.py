from os import cpu_count
from tracemalloc import take_snapshot

import aws_cdk
from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as _patterns
from aws_cdk import aws_elasticloadbalancingv2 as _elb
from aws_cdk import aws_iam as _iam
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct
from aws_cdk import aws_route53 as _route53
from aws_cdk import aws_certificatemanager as _cert
from aws_cdk import aws_route53_targets as _route53targets


class EcsClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        docker_image = self.node.try_get_context("envs")['prod']['docker_dir']

        # cfn_public_repository = _ecr.Repository(self, "MyCfnPublicRepository",
        #                         repository_name="mm_ecr_repo",
        #                         )
        
        prod_configs = self.node.try_get_context("envs")['prod']
        vpc_configs = self.node.try_get_context("envs")['prod']['vpc_configs']
        environment = self.node.try_get_context("envs")
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
        # route_table = ec2.CfnRouteTable(self,
        #                                 "MyCfnRouteTable",
        #                                 vpc_id=custom_vpc.vpc_id,
        #                             )

        # route_table.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # cfn_route = ec2.CfnRoute(self,
        #                          "MyCfnRoute",
        #                          gateway_id=custom_vpc.internet_gateway_id,
        #                          route_table_id=route_table.attr_route_table_id,
        #                          destination_cidr_block="0.0.0.0/0",
        #                     )

        # cfn_route.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # cfn_route_association = ec2.CfnSubnetRouteTableAssociation(self, 
        #                                                            "assoc1",
        #                                                            route_table_id=route_table.attr_route_table_id,
        #                                                            subnet_id=custom_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnets[0].subnet_id
           
        #                                                         )
        # cfn_route_association.apply_removal_policy(RemovalPolicy.DESTROY)
        

        # cfn_route_association2 = ec2.CfnSubnetRouteTableAssociation(self, 
        #                                                            "assoc2",
        #                                                            route_table_id=route_table.attr_route_table_id,
        #                                                            subnet_id=custom_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnets[1].subnet_id 
        #                                                         )
        # cfn_route_association2.apply_removal_policy(RemovalPolicy.DESTROY)
        
        
        # cfn_route_association3 = ec2.CfnSubnetRouteTableAssociation(self, 
        #                                                            "assoc3",
        #                                                            route_table_id=route_table.attr_route_table_id,
        #                                                            subnet_id=custom_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnets[2].subnet_id
        #                                                         )
        # cfn_route_association3.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # vpc_endpoint = ec2.InterfaceVpcEndpoint(self,
        #                                        "APIendpoint",
        #                                        vpc=custom_vpc,
        #                                        service=ec2.InterfaceVpcEndpointAwsService.APIGATEWAY
        # )

        # load_balancer = _elb.ApplicationLoadBalancer(self, 
        #                                             "MMelasticNetworkLB",
        #                                             vpc=custom_vpc,
        #                                             vpc_subnets=ec2.SubnetSelection(
        #                                                 subnet_type=ec2.SubnetType.PUBLIC
        #                                             ),
        #                                             internet_facing=True,
        #                                         )

        # zone = _route53.HostedZone.from_lookup(self,
        #                                         "hostedzone",
        #                                         domain_name="levi9masterclass.com",
        #                                     )

        # _route53.ARecord(self,
        #                 "apiv1.markomandic.levi9masterclass",
        #                  record_name="api.markomandic.levi9masterclass.com",
        #                  target=_route53.RecordTarget.from_alias(
        #                     _route53targets.LoadBalancerTarget(load_balancer),
        #                  ),
        #                  ttl=aws_cdk.Duration.seconds(300),
        #                  zone=zone)

        # cert = _cert.Certificate(self,
        #                         "certificate",
        #                         domain_name="*.markomandic.levi9masterclass.com",
        #                         validation=_cert.CertificateValidation.from_dns(zone))

        # cluster = ecs.Cluster(self, 
        #                       "FargateCPCluster",
        #                       vpc=custom_vpc,
        #                       enable_fargate_capacity_providers=True,
        #                       container_insights=True
        #                     )

        # # task_definition = ecs.FargateTaskDefinition(self, 
        # #                                             "TaskDef",
        # #                                             memory_limit_mib=512,
        # #                                             cpu=256,
        # #                                         )

        # task_definition = ecs.TaskDefinition(self,
        #                                      "taskdefinition",
        #                                      family="task",
        #                                      compatibility=ecs.Compatibility.EC2_AND_FARGATE,
        #                                      cpu="256",
        #                                      memory_mib="512",
        #                                      network_mode=ecs.NetworkMode.AWS_VPC)

        # task_definition.add_to_execution_role_policy(_iam.PolicyStatement(
        #                         resources=["*"],
        #                         actions= [
        #                                   "ecr:GetAuthorizationToken",
        #                                   "ecr:BatchCheckLayerAvailability",
        #                                   "ecr:GetDownloadUrlForLayer","ecr:BatchGetImage",
        #                                   "logs:CreateLogStream","logs:PutLogEvents"
        #                                 ],
        #                         ))

        # container = task_definition.add_container("swagger",
        #                                           image=ecs.ContainerImage.from_registry("446835144354.dkr.ecr.eu-west-1.amazonaws.com/markomandicecrrepo:latest"),
        #                                           memory_limit_mib=512,
        #                                           logging=ecs.AwsLogDriver(
        #                                             stream_prefix="mm-ecr"
        #                                         ),
        #                                     )
        # port_mapping = ecs.PortMapping(container_port=80)
        # container.add_port_mappings(port_mapping)
        
        # ecs_security_group = ec2.SecurityGroup(self,
        #                                        "ecs_sec_grp",
        #                                         vpc=custom_vpc,
        #                                         allow_all_outbound=True)


        # ecs_fargate_service = ecs.FargateService(self, 
        #                                         "FargateService",
        #                                         cluster=cluster,
        #                                         desired_count=1,
        #                                         task_definition=task_definition,
        #                                         assign_public_ip=True,
        #                                         vpc_subnets=ec2.SubnetSelection(
        #                                             subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
        #                                         ),
        #                                         capacity_provider_strategies=[ecs.CapacityProviderStrategy(
        #                                             capacity_provider="FARGATE_SPOT",
        #                                             weight=1
        #                                         ), ecs.CapacityProviderStrategy(
        #                                             capacity_provider="FARGATE",
        #                                             weight=2
        #                                         )],
        #                                         security_groups=[ecs_security_group]
        #                                     )

        # # listener.add_targets("fargate_target_group",
        # #                     port=80,
        # #                     targets=[ecs_fargate_service],
        # #                     deregistration_delay=aws_cdk.Duration.seconds(300)
        # #                     )
        # target_group_http = _elb.ApplicationTargetGroup(self,
        #                                                 "applicationtargetgrouphttp",
        #                                                 port=80,
        #                                                 vpc=custom_vpc,
        #                                                 protocol=_elb.ApplicationProtocol.HTTP,
        #                                                 target_type=_elb.TargetType.IP)
        # target_group_http.configure_health_check(
        #     path="/",
        #     protocol=_elb.ApplicationProtocol.HTTP
        # )

        # listener = load_balancer.add_listener("mmListenerRule",
        #                                       open=True,
        #                                       port=443,
        #                                       certificates=[cert]
        #                                     )

        # listener.add_target_groups("alb-listener-target-group",
        #                             target_groups=[target_group_http])


        # security_group_alb = ec2.SecurityGroup(self, 
        #                                            "mm-ecs-security-group",
        #                                            vpc=custom_vpc,
        #                                            allow_all_outbound=True
        #                                         )
                                                
        # security_group_alb.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))

        # load_balancer.add_security_group(security_group_alb)

        # ecs_security_group.connections.allow_from(security_group_alb,
        #                                           ec2.Port.all_tcp(),
        #                                           "ApplicationLoadBalancer")

        cluster = ecs.Cluster(self, 
                              "FargateCPCluster",
                              vpc=custom_vpc,
                              enable_fargate_capacity_providers=True,
                              container_insights=True
                            )

        task_definition = ecs.FargateTaskDefinition(self, 
                                                    "TaskDef",
                                                    memory_limit_mib=512,
                                                    cpu=256,
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
                                                  image=ecs.ContainerImage.from_registry("446835144354.dkr.ecr.eu-west-1.amazonaws.com/markomandicecrrepo:latest"),
                                                  logging=ecs.AwsLogDriver(
                                                    stream_prefix="mm-ecr"
                                                ),
                                            )

        port_mapping = ecs.PortMapping(container_port=80, host_port=80)
        container.add_port_mappings(port_mapping)

        ecs_fargate_service = ecs.FargateService(self, 
                                                "FargateService",
                                                cluster=cluster,
                                                task_definition=task_definition,
                                                assign_public_ip=True,
                                                vpc_subnets=ec2.SubnetSelection(
                                                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                                                ),
                                                capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                                                    capacity_provider="FARGATE_SPOT",
                                                    weight=1
                                                ), ecs.CapacityProviderStrategy(
                                                    capacity_provider="FARGATE",
                                                    weight=2
                                                )],
                                            )
        
        load_balancer = _elb.ApplicationLoadBalancer(self, 
                                                    "MMelasticNetworkLB",
                                                    vpc=custom_vpc,
                                                    internet_facing=True,
                                                )

        listener = load_balancer.add_listener("mmListenerRule",
                                              port=80,
                                            )
        
        security_group_fargate = ec2.SecurityGroup(self, 
                                                   "mm-ecs-security-group",
                                                   vpc=custom_vpc,
                                                   allow_all_outbound=True
                                                )
        
        security_group_fargate.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        listener.add_targets("fargate_target_group",
                            port=80,
                            targets=[ecs_fargate_service],
                            deregistration_delay=aws_cdk.Duration.seconds(300)
                            )
