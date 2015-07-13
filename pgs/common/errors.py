class BaseError(Exception):
    """Base class for all application errors."""
    pass


class InputFileError(BaseError):
    """Raised when there is trouble reading an input file."""
    pass


class InvalidServerError(BaseError):
    """Raised when a bad server identifier is given."""
    pass


class ServerStopError(BaseError):
    """Raised when a server does not stop."""
    pass


class DatabaseError(BaseError):
    """Raised when a database error is encountered."""
    pass
