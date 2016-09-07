# -*- coding: utf-8 -*-
import six
from six.moves.urllib.parse import urlsplit, urlunsplit

from modularodm.exceptions import (
    ValidationError,
    ValidationTypeError,
    ValidationValueError,
)

from bson import ObjectId

class Validator(object):

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class TypeValidator(Validator):

    def _as_list(self, value):

        if isinstance(value, (tuple, list)):
            return value
        return [value]

    def __init__(self, allowed_types, forbidden_types=None):
        self.allowed_types = self._as_list(allowed_types)
        self.forbidden_types = self._as_list(forbidden_types) if forbidden_types else []

    def __call__(self, value):

        for ftype in self.forbidden_types:
            if isinstance(value, ftype):
                self._raise(value)

        for atype in self.allowed_types:
            if isinstance(value, atype):
                return

        self._raise(value)

    def _raise(self, value):

        raise ValidationTypeError(
            'Received invalid value {} of type {}'.format(
                value, type(value)
            )
        )

validate_string = TypeValidator(six.string_types)
validate_integer = TypeValidator(
    allowed_types=int,
    forbidden_types=bool
)
validate_float = TypeValidator(float)
validate_boolean = TypeValidator(bool)
validate_objectid = TypeValidator(ObjectId)

from ..fields.lists import List
validate_list = TypeValidator(List)

import datetime
validate_datetime = TypeValidator(datetime.datetime)

# Adapted from Django RegexValidator
import re
class RegexValidator(Validator):

    def __init__(self, regex=None, flags=0):

        if regex is not None:
            self.regex = re.compile(regex, flags=flags)

    def __call__(self, value):

        if not self.regex.findall(value):
            raise ValidationError(
                u'Value must match regex {0} and flags {1}; received value <{2}>'.format(
                    self.regex.pattern,
                    self.regex.flags,
                    value
                )
            )

# Adapted from Django URLValidator
class URLValidator(RegexValidator):
    ul = ur'\u00a1-\uffff'  # unicode letters range, must be a unicode string

    # IP patterns
    ipv4_re = ur'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = ur'\[[0-9a-f:\.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = ur'[a-z' + ul + ur'0-9](?:[a-z' + ul + ur'0-9-]{0,61}[a-z' + ul + ur'0-9])?'
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = ur'(?:\.(?!-)[a-z' + ul + ur'0-9-]{1,63}(?<!-))*'
    tld_re = (
        ur'\.'                                # dot
        ur'(?!-)'                             # can't start with a dash
        ur'(?:xn--[a-z0-9]{1,59}'             # punycode labels (first for an eager regex match)
        ur'|[a-z' + ul + '-]{2,63})'          # or domain label
        ur'(?<!-)'                            # can't end with a dash
        ur'\.?'                               # may have a trailing dot
    )
    host_re = ur'(' + hostname_re + domain_re + tld_re + ur'|localhost)'

    regex = re.compile(
        ur'^(?:[a-z0-9\.\-\+]*)://'  # scheme is validated separately
        ur'(?:\S+(?::\S*)?@)?'  # user:pass authentication
        ur'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
        ur'(?::\d{2,5})?'  # port
        ur'(?:[/?#][^\s]*)?'  # resource path
        ur'\Z', re.IGNORECASE)
    message = 'Invalid URL'
    schemes = ['http', 'https', 'ftp', 'ftps']

    def __init__(self, schemes=None, **kwargs):
        super(URLValidator, self).__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def __call__(self, value):
        # Check first if the scheme is valid (if there is a scheme used)
        if '://' in value:
            scheme = value.split('://')[0].lower()
            if scheme not in self.schemes:
                raise ValidationError(self.message + ' ' + value)
        else:
            value = 'http://' + value # implicit scheme

        # Then check full URL
        try:
            super(URLValidator, self).__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain
            if value:
                try:
                    scheme, netloc, path, query, fragment = urlsplit(value)
                except ValueError:  # for example, "Invalid IPv6 URL"
                    raise ValidationError(self.message + ' ' + value)
                try:
                    netloc = netloc.encode('idna').decode('ascii')  # IDN -> ACE
                except UnicodeError:  # invalid domain part
                    raise e
                url = urlunsplit((scheme, netloc, path, query, fragment))
                super(URLValidator, self).__call__(url)
            else:
                raise
        else:
            # Now verify IPv6 in the netloc part
            host_match = re.search(r'^\[(.+)\](?::\d{2,5})?$', urlsplit(value).netloc)
            if host_match:
                potential_ip = host_match.groups()[0]
                try:
                    validate_ipv6_address(potential_ip)
                except ValidationError:
                    raise ValidationError(self.message, code=self.code)
            url = value

        # The maximum length of a full host name is 253 characters per RFC 1034
        # section 3.1. It's defined to be 255 bytes or less, but this includes
        # one byte for the length of the name and one byte for the trailing dot
        # that's used to indicate absolute names in DNS.
        if len(urlsplit(value).netloc) > 253:
            raise ValidationError(self.message, code=self.code)

class BaseValidator(Validator):

    compare = lambda self, a, b: a is not b
    clean = lambda self, x: x
    message = 'Ensure this value is %(limit_value)s (it is %(show_value)s).'
    code = 'limit_value'

    def __init__(self, limit_value):
        self.limit_value = limit_value

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'limit_value': self.limit_value, 'show_value': cleaned}
        if self.compare(cleaned, self.limit_value):
            raise ValidationValueError(self.message.format(**params))


class MaxValueValidator(BaseValidator):

    compare = lambda self, a, b: a > b
    message = 'Ensure this value is less than or equal to {limit_value}.'
    code = 'max_value'


class MinValueValidator(BaseValidator):

    compare = lambda self, a, b: a < b
    message = 'Ensure this value is greater than or equal to {limit_value}.'
    code = 'min_value'


class MinLengthValidator(BaseValidator):

    compare = lambda self, a, b: a < b
    clean = lambda self, x: len(x)
    message = 'Ensure this value has length of at least {limit_value} (it has length {show_value}).'
    code = 'min_length'


class MaxLengthValidator(BaseValidator):

    compare = lambda self, a, b: a > b
    clean = lambda self, x: len(x)
    message = 'Ensure this value has length of at most {limit_value} (it has length {show_value}).'
    code = 'max_length'
