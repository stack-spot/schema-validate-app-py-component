import boto3
import json
import pytest
from datetime import datetime
from uuid import uuid4
from botocore.stub import Stubber
from unittest import (mock, TestCase)
from plugin.domain.manifest import Manifest
from plugin.infrastructure.resource.aws.cdk.main import AwsCdk


class AwsCdkTest(TestCase, AwsCdk):

    @mock.patch("plugin.infrastructure.resource.aws.cdk.main.SDK", autospec=True)
    @mock.patch("plugin.infrastructure.resource.aws.services.route53.service.boto3", autospec=True)
    @mock.patch("plugin.infrastructure.resource.aws.cdk.engine.helpers.boto3", autospec=True)
    def setUp(self, mock_boto3_cf, mock_boto3_route53, mock_sdk) -> None:
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

        self.mock_cloud_service = mock_sdk.return_value
        self.mock_session = mock_boto3_cf.Session.return_value
        self.mock_cf = self.mock_session.client.return_value
        self.cf_client = boto3.client(
            "cloudformation", region_name="us-east-1")
        self.stubber_cf = Stubber(self.cf_client)
        self.stubber_cf.activate()

        self.mock_route53 = mock_boto3_route53.client.return_value
        self.route53_client = boto3.client(
            "route53", region_name="us-east-1")
        self.stubber_route53 = Stubber(self.route53_client)
        self.stubber_route53.activate()
        return super().setUp()

    def mock_create_stack(self, stack_name: str, stack_template: str):
        response = {
            'StackId': uuid4().__str__()
        }

        expected_params = {
            'StackName': stack_name,
            'TemplateBody': json.dumps(stack_template),
            'OnFailure': 'ROLLBACK',
            'Capabilities': ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        }

        self.stubber_cf.add_response('create_stack', response, expected_params)

        mocked_response = self.cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=json.dumps(stack_template),
            OnFailure='ROLLBACK',
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )

        return mocked_response

    def mock_describe_stack_events(self, stack_name: str, stack_template: dict):

        resource_id = list(stack_template["Resources"].keys())[0]

        events_finish = {
            "StackEvents": [
                {
                    "StackId": uuid4().__str__(),
                    "EventId": "1",
                    "StackName": stack_name,
                    "LogicalResourceId": resource_id,
                    "PhysicalResourceId": resource_id,
                    "ResourceType": ".",
                    "Timestamp": datetime(2021, 1, 1),
                    "ResourceStatus": "CREATE_COMPLETE",
                    "ResourceStatusReason": "...",
                    "ResourceProperties": ".",
                    "ClientRequestToken": "."
                },
            ],
            "NextToken": "string"
        }

        self.stubber_cf.add_response("describe_stack_events", events_finish, {
            "StackName": stack_name})

        mocked_response = self.cf_client.describe_stack_events(
            StackName=stack_name
        )

        return mocked_response

    def mock_stack_template(self, x: int):
        return {
            "Resources": {
                f"resource-{x}": {
                    "Type": "AWS::Resource",
                    "Properties": {}
                }
            }
        }

    def mock_get_hosted_zone(self, zone_id: str):
        response = {
            'HostedZone': {
                'Id': zone_id,
                'Name': "hosted.example.com",
                'CallerReference': 'caller',
                'Config': {
                    'Comment': "No comment",
                    'PrivateZone': True
                },
                'ResourceRecordSetCount': 1,
                'LinkedService': {
                    'ServicePrincipal': 'principal',
                    'Description': 'Description'
                }
            },
            'DelegationSet': {
                'Id': '123',
                'CallerReference': 'caller_ref',
                'NameServers': [
                    'ns1.server.com',
                ]
            },
            'VPCs': [
                {
                    'VPCRegion': 'us-east-1',
                    'VPCId': self.manifest.schema_validate.vpc_endpoint.vpc_id
                },
            ]
        }

        expected_params = {
            'Id': zone_id
        }

        self.stubber_route53.add_response(
            'get_hosted_zone', response, expected_params)

        mocked_response = self.route53_client.get_hosted_zone(Id=zone_id)

        return mocked_response

    def get_exception_from_s3_head_bucket(self, exception: int, bucket_name: str):
        s3 = boto3.resource('s3')
        stubber = Stubber(s3.meta.client)
        stubber.activate()

        stubber.add_client_error("head_bucket",
                                 service_error_code=exception,
                                 service_message=exception,
                                 http_status_code=404)
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except Exception as error:
            return error
    
    @pytest.mark.skip(reason="no way of currently testing this")
    @mock.patch("plugin.infrastructure.resource.aws.cdk.engine.helpers.is_created_resource", autospec=True)
    @mock.patch("plugin.infrastructure.resource.aws.services.main.boto3", autospec=True)
    @mock.patch("plugin.infrastructure.resource.aws.services.s3.service.boto3", autospec=True)
    @mock.patch("plugin.infrastructure.resource.aws.services.route53.service.boto3", autospec=True)
    @mock.patch("plugin.infrastructure.resource.aws.cdk.engine.helpers.boto3", autospec=True)
    def test_create_resources_with_aws_cdk(self, mock_boto3_cf, mock_boto3_route53, mock_boto3_s3, mock_boto3_sts, mock_created_resource):
        mock_sts = mock_boto3_sts.client.return_value

        mock_sts.get_caller_identity.side_effect = [
            {
                "Account": "12345678912"
            } for _ in range(2)
        ]

        mock_s3 = mock_boto3_s3.resource.return_value

        mock_s3.meta.client.head_bucket.side_effect = [
            True,
            True,
            self.get_exception_from_s3_head_bucket(
                exception=404, bucket_name="my-bucket"),
            self.get_exception_from_s3_head_bucket(
                exception=404, bucket_name="my-bucket")
        ]

        mock_route53 = mock_boto3_route53.client.return_value
        mock_route53.get_hosted_zone.side_effect = [
            self.mock_get_hosted_zone(
                zone_id=self.manifest.schema_validate.record.zone_id
            )
        ]

        mock_session = mock_boto3_cf.Session.return_value
        mock_cf = mock_session.client.return_value

        mock_cf.create_stack.side_effect = [
            self.mock_create_stack(
                stack_name=self.manifest.schema_validate.name,
                stack_template=self.mock_stack_template(i)
            ) for i in range(3)
        ]

        mock_cf.describe_stack_events.side_effect = [
            self.mock_describe_stack_events(
                stack_name=self.manifest.schema_validate.name,
                stack_template=self.mock_stack_template(i)
            ) for i in range(3)
        ]

        mock_created_resource.side_effect = [True, True, True]

        self.create_setup(api_gateway=self.manifest.schema_validate)

        # When bucket assets already exists
        self.create_assets(api_gateway=self.manifest.schema_validate)

        self.create_function(
            name=self.manifest.schema_validate.name,
            registry=self.manifest.schema_validate.registry,
            region=self.manifest.schema_validate.region
        )

        self.mock_cloud_service.check_bucket.side_effect = [False, False]

        # When bucket assets do not exists
        self.create_assets(api_gateway=self.manifest.schema_validate)
