class ValidationError(Exception):
    """ Base class for exceptions raised during validation. Should not raised
    directly. """
    pass


class ValidationTypeError(ValidationError, TypeError):
    """ Raised during validation if explicit type check failed """
    pass


class ValidationValueError(ValidationError, ValueError):
    """ Raised during validation if the value of the input is unacceptable, but
     the type is correct """
    pass