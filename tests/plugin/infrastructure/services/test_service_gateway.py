from datetime import datetime
from botocore.stub import Stubber
from plugin.infrastructure.resource.aws.services.gateway import ApiGatewayService
import boto3



api_gateway = boto3.client("apigateway", region_name="us-east-1")
stubber = Stubber(api_gateway)

class TestGatewayServicer(ApiGatewayService):
    __test__ = False

    def __init__(self):
        self.api_gateway = api_gateway


def test_gateway_init():
    service = ApiGatewayService("us-east-1")
    assert str(type(service.api_gateway)) == str(type(api_gateway))


def test_create_custom_domain(capsys):
    stubber.add_response(
            "create_domain_name",
            {
                "domainName": "domain"
                })
    stubber.activate()
    gateway_servicer = TestGatewayServicer()
    gateway_servicer.create_custom_domain("domain", "cert", "_type")
    captured = capsys.readouterr()
    assert captured.out == "domain created\n"


def test_create_custom_domain_error(caplog):
    stubber.add_client_error("create_domain_name", service_error_code="ClientError")
    stubber.activate()
    gateway_servicer = TestGatewayServicer()
    gateway_servicer.create_custom_domain("domain", "cert", "_type")
    assert "ClientError" in caplog.records[0].message


def test_not_exists_api_gateway():
    response = {
            'position': 'string',
            'items': [
                {
                    'id': 'string',
                    'name': 'not-found',
                    'description': 'string',
                    'createdDate': datetime(2015, 1, 1),
                    'version': 'string',
                    'warnings': [
                        'string',
                        ],
                    'binaryMediaTypes': [
                        'string',
                        ],
                    'minimumCompressionSize': 123,
                    'apiKeySource': 'HEADER',
                    'endpointConfiguration': {
                        'types': [ 'REGIONAL' ],
                        'vpcEndpointIds': [ 'string' ]
                        },
                    'policy': 'string',
                    'tags': {
                        'string': 'string'
                        },
                    'disableExecuteApiEndpoint': True
                    },
                ]
            }
    stubber.add_response("get_rest_apis", response)
    stubber.activate()
    gateway_servicer = TestGatewayServicer()
    res = gateway_servicer.not_exists_api_gateway("gw-api")
    assert res is True


def test_not_exists_api_gateway_exists():
    response = {
            'position': 'string',
            'items': [
                {
                    'id': 'string',
                    'name': 'gw-api',
                    'description': 'string',
                    'createdDate': datetime(2015, 1, 1),
                    'version': 'string',
                    'warnings': [
                        'string',
                        ],
                    'binaryMediaTypes': [
                        'string',
                        ],
                    'minimumCompressionSize': 123,
                    'apiKeySource': 'HEADER',
                    'endpointConfiguration': {
                        'types': [ 'REGIONAL' ],
                        'vpcEndpointIds': [ 'string' ]
                        },
                    'policy': 'string',
                    'tags': {
                        'string': 'string'
                        },
                    'disableExecuteApiEndpoint': True
                    },
                ]
            }
    stubber.add_response("get_rest_apis", response)
    stubber.activate()
    gateway_servicer = TestGatewayServicer()
    res = gateway_servicer.not_exists_api_gateway("gw-api")
    assert res is False


def test_not_exists_api_gateway_error(caplog):
    stubber.add_client_error("get_rest_apis", service_error_code="ClientError")
    stubber.activate()
    gateway_servicer = TestGatewayServicer()
    gateway_servicer.not_exists_api_gateway("gw")
    assert "ClientError" in caplog.records[0].message
