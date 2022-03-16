import string
import random
from plugin.usecase.schemavalidate.interface import DataSchemaValidateInterface
import pytest
from unittest import (mock, TestCase)
from plugin.infrastructure.resource.aws.cdk.main import AwsCdk
from plugin.usecase.schemavalidate.main import DataSchemaValidateUseCase
from plugin.domain.manifest import Manifest, SchemaValidate


class MockDataApiGatewayUseCase(DataSchemaValidateInterface):

    def __init__(self) -> None:
        pass

    def apply(self, api_gateway: SchemaValidate):
        return super().apply(api_gateway=api_gateway)


class CreateDataApiGatewayTest(TestCase):

    @staticmethod
    def __random_string(letter, size: int):
        return ''.join(random.choice(letter) for _ in range(size))

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            data_api_gateway_use_case_mock = MockDataApiGatewayUseCase()
            data_api_gateway_use_case_mock.create(
                api_gateway=self.manifest.api_gateway)

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

    @pytest.mark.skip(reason="no way of currently testing this")
    @mock.patch('plugin.usecase.apigateway.main.create_lambda_package', return_value=None)
    @mock.patch("plugin.infrastructure.resource.aws.cdk.main.AwsCdk.create_function", return_value=None)
    @mock.patch("plugin.infrastructure.resource.aws.cdk.main.AwsCdk.create_setup", return_value=None)
    @mock.patch("plugin.infrastructure.resource.aws.cdk.main.AwsCdk.create_assets", return_value=None)
    @mock.patch("plugin.usecase.apigateway.main.SDK", autospec=True)
    def test_if_create_data_api_gateway_works(self, mock_service, _cdk_assets, _cdk_setup, _cdk_lambda_function, _package):
        name = self.__random_string(
            letter=string.ascii_letters,
            size=18)
        self.manifest.api_gateway.name = f"{name}_test"
        mock_cloud_service = mock_service.return_value
        mock_cloud_service.account_id.return_value = random.randint(
            1000000, 9000000)
        mock_cloud_service.upload_object.side_effect = [None, None]
        mock_cloud_service.not_exists_record.side_effect = [True, True]
        mock_cloud_service.not_exists_lambda.side_effect = [True, True]
        result = DataSchemaValidateUseCase(cloud=AwsCdk()).apply(
            api_gateway=self.manifest.api_gateway)
        assert result == True
