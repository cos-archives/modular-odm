# todo: make this do something or use built-in exception?
class ValidationError(Exception):
    pass

class StringValidator(object):

    def __call__(self, value):

        if type(value) not in [str, unicode]:
            raise ValidationError('Not a valid string: <{0}>'.format(value))

class MinLengthValidator(StringValidator):

    def __init__(self, min_length):

        self.min_length = min_length

    def __call__(self, value):

        super(MinLengthValidator, self).__call__(value)
        if len(value) < self.min_length:
            raise ValidationError(
                'Length must be at least {0}; received value <{1}> of length {2}'.format(
                    self.min_length,
                    value,
                    len(value)
                )
            )

class MaxLengthValidator(StringValidator):

    def __init__(self, max_length):

        self.max_length = max_length

    def __call__(self, value):

        super(MaxLengthValidator, self).__call__(value)
        if len(value) > self.max_length:
            raise ValidationError(
                'Length must be less than or equal to {0}; received value <{1}> of length {2}'.format(
                    self.max_length,
                    value,
                    len(value)
                )
            )


# Adapted from Django RegexValidator
import re
class RegexValidator(StringValidator):

    def __init__(self, regex, flags=0):

        self.regex = re.compile(regex, flags=flags)

    def __call__(self, value):

        super(RegexValidator, self).__call__(value)
        if not self.regex.search(value):
            raise ValidationError(
                'Value must match regex {0} and flags {1}; received value <{2}>'.format(
                    self.regex.pattern,
                    self.regex.flags,
                    value
                )
            )

import datetime
class DateTimeValidator(object):

    def __call__(self, value):

        if not isinstance(value, datetime.datetime):
            raise ValidationError(
                'Value must be a datetime object; received value <{0}>'.format(
                    value
                )
            )
