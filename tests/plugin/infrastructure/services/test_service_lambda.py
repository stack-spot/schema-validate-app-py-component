from botocore.stub import Stubber
from plugin.infrastructure.resource.aws.services.lambda_service import LambdaResource
import boto3


session = boto3.Session()
_lambda = session.client("lambda", region_name="us-east-1")
stubber = Stubber(_lambda)

class TestLambdaResource(LambdaResource):
    __test__ = False

    def __init__(self):
        self._lambda = _lambda


def test_not_exists_lambda_exists():
    response = {
            'Configuration': {
                'FunctionName': 'lambdaFunc',
                }
            }
    stubber.add_response(
            "get_function",
            response,
            { "FunctionName": "lambdaFunc" })
    stubber.activate()
    _lambda_resource = TestLambdaResource()
    res = _lambda_resource.not_exists_lambda("lambdaFunc")
    assert res is False


def test_not_exists_lambda():
    stubber.add_client_error("get_function", service_error_code="ResourceNotFoundException")
    stubber.activate()
    _lambda_resource = TestLambdaResource()
    res = _lambda_resource.not_exists_lambda("lambdaFunc")
    assert res is True


def test_not_exists_lambda_unexpected():
    stubber.add_client_error("get_function") 
    stubber.activate()
    _lambda_resource = TestLambdaResource()
    res = _lambda_resource.not_exists_lambda("lambdaFunc")
    assert res is False
