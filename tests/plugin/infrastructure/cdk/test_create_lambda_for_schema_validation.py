import string
import random
import pytest
from aws_cdk import core
from unittest import TestCase
from plugin.infrastructure.resource.aws.cdk.stacks.lambda_stack import Lambda
from plugin.domain.manifest import Manifest
import json


class CdkStackLambdaSchemaValidation(TestCase):

    @staticmethod
    def __random_string(letter, size: int):
        return ''.join(random.choice(letter) for _ in range(size))

    @pytest.fixture(autouse=True)
    def plugin_manifest(self):
        self.manifest = Manifest({
            "api_gateway": {
                "name": "my-gateway",
                "region": "us-east-1",
                "type": "PRIVATE",
                "auth": {
                    "iam_auth": True,
                    "api_key": True
                },
                "registry": "registry_xxxxxxx",
                "record": {
                    "zone_id": "ZONEID12341234"
                },
                "vpc_endpoint": {
                    "vpc_id": "vpc_xxxxxxx",
                    "subnets_ids": ["sub_xxxxxxx"],
                    "security_group": {
                        "ip_blocks_sg": ["10.0.0.0/21"],
                        "eg_blocks_sg": ["0.0.0.0/0"]
                    }
                }
            }
        })

    @pytest.fixture(autouse=True)
    def cdk_app(self):
        self.app = core.App()
        self.stack_name = f"create-{self.__random_string(letter=string.ascii_letters,size=10)}-api-functions-"
        self.stack = Lambda(self.app, self.stack_name)

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_if_create_lambda_schema_validation_works(self):
        name = self.__random_string(
            letter=string.ascii_letters,
            size=18)
        self.manifest.schema_validate.name = f"{name}_test"

        self.stack.create_bucket_for_lambda_assets(
            name="my-bucket-to-put-lambda-zip-file"
        )

        self.stack.create_lambda_for_schema_validation(
            name, self.manifest.schema_validate.name,  self.manifest.schema_validate.region
        )
