class ValidationError(Exception):
    pass


class ValidationTypeError(ValidationError, TypeError):
    """ Raised during validation if explicit type check failed."""
    pass