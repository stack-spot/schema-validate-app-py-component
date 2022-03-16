from abc import ABCMeta, abstractmethod

class LambdaResourceInterface(metaclass=ABCMeta):
    """
    TO DO
    """

    @abstractmethod
    def not_exists_lambda(self, name: str) -> None:
        raise NotImplementedError
