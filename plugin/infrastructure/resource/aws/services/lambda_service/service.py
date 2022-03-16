from .interface import LambdaResourceInterface
from botocore.client import ClientError
import boto3
from plugin.utils.logging import logger


class LambdaResource(LambdaResourceInterface):
    """
    TO DO

    Args:
        LambdaResourceInterface ([type]): [description]
    """

    def __init__(self, region: str):
        session = boto3.Session()
        self._lambda = session.client(
                "lambda", region_name=region)

    def not_exists_lambda(self, name: str):
        try:
            self._lambda.get_function(FunctionName=name)
            return False
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return True
            logger.error(
                    "Unexpected error while getting function: %s", e)
            return False
