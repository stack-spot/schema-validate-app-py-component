from aws_cdk import core as cdk

from .lambda_stack import Lambda 
from .api_stack import ApiGateway

class Stack(Lambda, ApiGateway):
    """
    TO DO
    Args:
        ApiGateway ([type]): [description]
    """

    def __init__(self, scope: cdk.Construct,
                 construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
