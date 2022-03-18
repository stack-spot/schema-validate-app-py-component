from plugin.domain.exceptions import HasFailedEventException, RestAPINotFoundException
from .interface import ApiGatewayInterface
from botocore.client import ClientError
from plugin.utils.logging import logger
import boto3


class ApiGatewayService(ApiGatewayInterface):
    """
    TO DO

    Args:
        ApiGatewayInterface ([type]): [description]
    """
    def __init__(self, region: str):
        self.api_gateway = boto3.client('apigateway', region_name=region)


    def get_rest_api_by_name(self, api_name: str):
        try:
            res = self.api_gateway.get_rest_apis()
            for r in res["items"]:
                if r["name"] == api_name:
                    logger.info("Rest api %s, found", api_name)
                    return r
            return None

        except ClientError as err:
            logger.error(
                    "Unexpected error while get rest apis", err)


    def get_api_resource_id(self, api_name: str, name: str):
        try:
            rest_api = self.get_rest_api_by_name(api_name)
            if rest_api is not None:
                response = self.api_gateway.get_resources(restApiId=rest_api["id"])
                resource = {}
                for r in response["items"]:
                    if r.get("pathPart") == name:
                        return { **r, "api_id": rest_api["id"] }
                    elif r.get("path") == "/":
                        resource = r
                return { **resource, "api_id": rest_api["id"] }
            else:
                raise RestAPINotFoundException(f'Rest API {api_name} not found')


        except ClientError as err:
            logger.error(
                    "Unexpected error while get api resources: %s", err)


    def create_custom_domain(self, domain_name: str, cert_arn: str, type_: str):
        try:
            response = self.api_gateway.create_domain_name(
                    domainName=domain_name,
                    certificateArn=cert_arn,
                    securityPolicy='TLS_1_2',
                    endpointConfiguration={'types': [type_]}
                    )
            print(response["domainName"], 'created')
        except ClientError as err:
            logger.error(
                    "Unexpected error while creating custom domain: %s", err)


    def not_exists_api_gateway(self, name: str):
        try:
            res = self.api_gateway.get_rest_apis()
            items = res["items"]
            response = True
            for item in items: 
                if item["name"] == name:
                    response = False
                    break
            return response
        except ClientError as err:
            logger.error(
                    "Unexpected error while check api gateway exists: %s", err)
            return None
