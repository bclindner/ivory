class ConfigurationError(Exception):
    """
    Generic exception for config problems.

    No derivative of this should be necessary - throw a ConfigurationError in
    any case and Ivory should exit after printing the message provided in the
    error.
    In the future I may extend this by having it provide the name of the key
    it failed on.
    """

class DriverError(Exception):
    """
    Generic base exception for Driver problems.
    """

class DriverNetworkError(DriverError):
    """
    Exception for network errors a Driver might encounter.

    Ivory currently assumes these network errors are temporary, and will
    attempt to retry when this error is raised.
    """

class DriverAuthorizationError(DriverError):
    """
    Exception raised if the driver does not have access to something it needs
    using the provided credentials.
    """

class RuleError(Exception):
    """
    Generic base exception for Rule problems.
    """

class PunishmentNotImplementedError(NotImplementedError):
    """
    Exception for when a punishment type is not implemented by a Driver.
    """