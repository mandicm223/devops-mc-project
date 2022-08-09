from cgitb import handler
from weakref import proxy
from aws_cdk import aws_iam as iam
from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as _api
from aws_cdk import aws_dynamodb as _dynamodb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _log
from constructs import Construct


class LambdaApiDynamoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        prod_configs = self.node.try_get_context("envs")['prod']
        lambdafunc = prod_configs['lambdafunc']

        table = _dynamodb.Table(self, 
                                "Table",
                                partition_key=_dynamodb.Attribute(name="id", 
                                type=_dynamodb.AttributeType.STRING),
                                table_name="lambda_api_table"
                            )

        lambda_func = _lambda.Function(self, 
                                       'HelloHandlerpost',
                                       runtime=_lambda.Runtime.PYTHON_3_9,
                                       code=_lambda.AssetCode(lambdafunc),
                                       handler='lambda_dynamo.handler',
                                    )
    

        lambda_lg = _log.LogGroup(self, 
                                  "lambda_mm_loggroup",
                                  log_group_name=f"/aws/lambda/{lambda_func.function_name}",
                                  removal_policy=RemovalPolicy.DESTROY
                                )
        
        table.grant_read_write_data(lambda_func)

        rest_api_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
                actions=["execute-api:*"],
                principals=[iam.AnyPrincipal()],
                resources=["execute-api:/*"],
                effect=iam.Effect.ALLOW,
                )]  
                )
        deny_policy =iam.PolicyStatement(
                actions=["execute-api:Invoke"],
                principals=[iam.AnyPrincipal()],
                resources=["execute-api:/*"],
                effect=iam.Effect.DENY,

                ### uradi da bude samo za endpoint "aws:SourceVpce": vpcEndpoint.vpcEndpointId
                )
        # deny_policy.add_condition("StringNotEquals", {"aws:SourceVpce": vpcEndpoint.vpc_endpoint_id})
        rest_api_policy.add_statements(deny_policy)


        api_gateway = _api.RestApi(self, 
                                  'apiGateway',
                                   endpoint_types=[_api.EndpointType.PRIVATE],
                                   policy=rest_api_policy,
                                )

        post = api_gateway.root.resource_for_path("/api/v1/createPerson")
        get = api_gateway.root.resource_for_path("/api/v1/getPerson")

        get.add_method("GET", _api.LambdaIntegration(lambda_func)) # GET /items
        post.add_method("POST", _api.LambdaIntegration(lambda_func)) # POST /items
