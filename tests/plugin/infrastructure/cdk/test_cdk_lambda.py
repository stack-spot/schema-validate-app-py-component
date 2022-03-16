from aws_cdk import (core, assertions)
from plugin.infrastructure.resource.aws.cdk.stacks.lambda_stack import Lambda


def test_aws_cdk_create_lambda_assets():
    app = core.App()
    stack_name = "create-lambda-assets-stack"
    lambda_stack = Lambda(app, stack_name)
    bucket_name = "bucket-name"

    lambda_stack.create_bucket_for_lambda_assets(bucket_name)

    template = assertions.Template.from_stack(lambda_stack)
    template.has_resource_properties("AWS::S3::Bucket", {
        "BucketName": bucket_name,
        "BucketEncryption": {
            "ServerSideEncryptionConfiguration": [
                {
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            },
        }) 

