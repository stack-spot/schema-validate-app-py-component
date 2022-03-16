import boto3
import sys
from botocore.exceptions import UnauthorizedSSOTokenError
from botocore.client import BaseClient, ClientError
from plugin.utils.logging import logger
from .s3 import S3
from .gateway import ApiGateway
from .lambda_service import Lambda


class SDK(S3, ApiGateway, Lambda):
    """
    TODO
    """
    client: BaseClient

    @property
    def account_id(self):
        try:
            client = boto3.client('sts')
            return client.get_caller_identity().get('Account')
        except UnauthorizedSSOTokenError as sso_error:
            logger.error(sso_error.fmt)
            sys.exit(1)
        except ClientError as err:
            logger.error(err)
            sys.exit(1)
