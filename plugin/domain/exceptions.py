#!/usr/bin/python3


class CLIError(Exception):
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

class HasFailedEventException(CLIError):
    """
    Has Failed Event Exception.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Stack has failed event."):
        self.message = message
        super().__init__(self.message)

class ManifestPrivateVpcEndpointNotFound(CLIError):
    """
    Already Exist Registry.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, logger, message="Vpc Endpoint configuration was not found, when type set to PRIVATE the Vpc endpoint becomes mandatory."):
        logger.error(message)
        self.message = message
        super().__init__(self.message)
        
class ManifestPrivateCustomDomainNotFound(CLIError):
    """
    Already Exist Registry.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, logger, message="Custom Domain configuration was not found, when type set to EDGE the Custom Domain becomes mandatory."):
        logger.error(message)
        self.message = message
        super().__init__(self.message)

class ManifestEdgeVpcEndpointNotRequired(CLIError):
    """
    Already Exist Registry.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, logger, message="When type set to EDGE the Vpc endpoint not required."):
        logger.error(message)
        self.message = message
        super().__init__(self.message)
