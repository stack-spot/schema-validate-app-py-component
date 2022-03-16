from abc import ABCMeta, abstractmethod
from plugin.domain.manifest import SchemaValidate


class DataSchemaValidateCloudInterface(metaclass=ABCMeta):
    @abstractmethod
    def create_assets(self, schema_validate: SchemaValidate):
        """
        TO DO
        """
        raise NotImplementedError


    @abstractmethod
    def create_function(self, name: str, registry: str, region: str):
        """
        TO DO
        """
        raise NotImplementedError


    @abstractmethod
    def create_api_resource(self, schema_validate: SchemaValidate, resource: dict):
        """
        TO DO
        """
        raise NotImplementedError


