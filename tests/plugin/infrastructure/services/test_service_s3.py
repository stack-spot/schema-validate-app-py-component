from botocore.stub import Stubber
from plugin.infrastructure.resource.aws.services.s3.service import S3Resource
import boto3


s3 = boto3.resource('s3').meta.client
stubber = Stubber(s3)

class TestS3Resource(S3Resource):
    __test__ = False

    def __init__(self):
        self.s3 = s3

def test_upload_object_forbidden(capsys):
    stubber.add_client_error(
            method="head_object",
            service_error_code="403"
            )
    stubber.activate()
    s3_resource = TestS3Resource()
    s3_resource.upload_object("/", "bucket-name", "package")
    captured = capsys.readouterr()

    assert captured.out == "Access to Private Bucket bucket-name is Forbidden!\n"


def test_check_bucket():
    stubber.add_response("head_bucket", {})
    stubber.activate()
    s3_resource = TestS3Resource()
    is_exists_bucket = s3_resource.check_bucket("bucket-name")

    assert is_exists_bucket == True


def test_check_bucket_forbidden():
    stubber.add_client_error(
            method="head_bucket",
            service_error_code="403"
            )
    stubber.activate()
    s3_resource = TestS3Resource()
    is_exists_bucket = s3_resource.check_bucket("bucket-name")

    assert is_exists_bucket == True


def test_check_bucket_not_found():
    stubber.add_client_error(
            method="head_bucket",
            service_error_code="404"
            )
    stubber.activate()
    s3_resource = TestS3Resource()
    is_exists_bucket = s3_resource.check_bucket("bucket-name")

    assert is_exists_bucket == False


def test_check_bucket_unexpected():
    stubber.add_client_error(
            method="head_bucket",
            service_error_code="401"
            )
    stubber.activate()
    s3_resource = TestS3Resource()
    is_exists_bucket = s3_resource.check_bucket("bucket-name")

    assert is_exists_bucket == False
