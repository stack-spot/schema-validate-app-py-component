from abc import ABCMeta, abstractmethod


class ApiGatewayInterface(metaclass=ABCMeta):
    """
    TO DO
    """

    @abstractmethod
    def create_custom_domain(self, domain_name: str, cert_arn: str, type_: str):
        raise NotImplementedError


    @abstractmethod
    def not_exists_api_gateway(self, name: str):
        raise NotImplementedError
