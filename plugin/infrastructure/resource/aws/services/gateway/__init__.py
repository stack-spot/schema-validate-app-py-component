from .service import ApiGatewayService


class ApiGateway:
    """
    TO DO
    """

    @staticmethod
    def not_exists_api_gateway(name: str, region: str):
        return ApiGatewayService(region).not_exists_api_gateway(name)


    @staticmethod
    def create_custom_domain(domain_name: str, cert_arn: str, type_: str, region: str):
        ApiGatewayService(region).create_custom_domain(domain_name, cert_arn, type_)


    @staticmethod
    def get_api_resource_id(api_name: str, name: str, region: str) -> dict: 
        return ApiGatewayService(region).get_api_resource_id(api_name, name)
