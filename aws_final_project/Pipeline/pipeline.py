from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep


class AwsFinalProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        environment = self.node.try_get_context("envs")
        first_name_last_name = self.node.try_get_context("envs")['prod']['first_last_name']

        pipeline = CodePipeline(self, "Pipeline",
                                pipeline_name=f"{environment}-pipeline-{first_name_last_name}-masterclass",
                                synth=ShellStep("Synth",
                                                input=CodePipelineSource.git_hub("mandicm223/devops-mc-project", "main"),)
                                )

