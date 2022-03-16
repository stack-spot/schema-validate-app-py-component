from abc import ABCMeta, abstractmethod
from plugin.domain.manifest import SchemaValidate


class DataSchemaValidateInterface(metaclass=ABCMeta):
    """
    A Data Lake stack is an infrastructure base that creates an environment
    to store data in a structured and/or semi-structured way, this plugin
    has the following features:

        Data repository
        Taxonomy
        Gateway
    """
    @abstractmethod
    def apply(self, schema_validate: SchemaValidate):
        raise NotImplementedError
