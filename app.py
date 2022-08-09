#!/usr/bin/env python3

from platform import node
import aws_cdk as cdk

from aws_final_project.aws_final_project_stack import AwsFinalProjectStack
from aws_final_project.Networking.networking import NetworkingtStack
from aws_final_project.LambdaApiDynamo.lambda_api_dynamo import LambdaApiDynamoStack
from aws_final_project.EcsCluster.ecs_cluster import EcsClusterStack

# env=cdk.Environment(account=app.node.try_get_context('envs')['prod']['account'], region=app.node.try_get_context('envs')['prod']['region'])
env_EU = cdk.Environment(account="446835144354", region="eu-west-1")

app = cdk.App()
NetworkingtStack(app, "networking-stack")
EcsClusterStack(app, "ecs-cluster-stack", env=env_EU)
LambdaApiDynamoStack(app, "lambda-api-dynamo-stack")


app.synth()
