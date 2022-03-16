#!/usr/bin/python3


class APIError(Exception):
    """
    Generic Exception.
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Something Went Wrong!"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)


class PutRecordError(APIError):
    """
    Exception for when could not put a record with boto3 sdk.
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Couldn't put record."):
        self.message = message
        super().__init__(self.message)
