import boto3
from botocore.stub import Stubber
from plugin.domain.manifest import Manifest
from plugin.infrastructure.resource.aws.services.s3.interface import S3Interface, S3ResourceInterface
from plugin.infrastructure.resource.aws.services.s3.service import S3Resource
import pytest
import random
import string
from unittest import (mock, TestCase)


class MockS3Resource(S3ResourceInterface):

    def __init__(self) -> None:
        pass

    def upload_object(self, path: str, bucket_name: str, package: str) -> None:
        return super().upload_object(path=path, bucket_name=bucket_name, package=package)

    def check_bucket_object(self, object_key: str, bucket_name: str) -> bool:
        return super().check_bucket_object(object_key=object_key, bucket_name=bucket_name)


class S3ResourceTest(TestCase):

    @mock.patch("plugin.infrastructure.resource.aws.services.s3.service.boto3", autospec=True)
    def setUp(self, mock_boto3) -> None:
        self.mock_session = mock_boto3.Session.return_value
        self.mock_s3 = self.mock_session.client.return_value
        self.s3_resource = S3Resource()
        self.s3 = boto3.resource("s3")
        self.stubber = Stubber(self.s3.meta.client)
        self.stubber.activate()

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

