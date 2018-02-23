import os

class SigningError(Exception):
    """
    Base Class for bluepea exceptions
    To use   raise BluepeaError("Error: message")
    """


class ValidationError(SigningError):
    """
    Validation related errors
    Usage:
        raise ValidationError("error message")
    """