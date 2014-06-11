# -*- coding: utf-8 -*-

from nose.tools import *

from modularodm import StoredObject, fields
from modularodm.exceptions import ValidationValueError

from tests.base import ModularOdmTestCase


class TestSchemaValidation(ModularOdmTestCase):

    def define_objects(self):

        def validate_schema(record):
            if record.value1 > record.value2:
                raise ValidationValueError

        class Schema(StoredObject):

            _id = fields.IntegerField(primary=True)
            value1 = fields.IntegerField()
            value2 = fields.IntegerField()

            _meta = {
                'validators': [validate_schema],
            }

        return Schema,

    def test_save_valid(self):
        record = self.Schema(_id=1, value1=2, value2=3)
        try:
            record.save()
        except ValidationValueError:
            assert False

    def test_save_invalid(self):
        record = self.Schema(_id=1, value1=3, value2=2)
        with assert_raises(ValidationValueError):
            record.save()
