# -*- coding: utf-8 -*-

import os.path
import json

from modularodm import StoredObject
from modularodm.exceptions import ValidationError
from modularodm.fields import StringField, IntegerField
from modularodm.validators import URLValidator

from tests.base import ModularOdmTestCase

class UrlValueValidatorTestCase(ModularOdmTestCase):

    def test_url(self):
        basepath = os.path.dirname(__file__)
        url_data_path = os.path.join(basepath, 'urlValidatorTest.json')
        with open(url_data_path) as url_test_data:
            data = json.load(url_test_data)

        class Foo(StoredObject):
            _id = IntegerField()
            url_field = StringField(
                list=False,
                validate=[URLValidator()]
            )

        Foo.set_storage(self.make_storage())
        test_object = Foo()

        for urlTrue in data['testsPositive']:
            test_object.url_field = urlTrue
            test_object.save()

        for urlFalse in data['testsNegative']:
            test_object.url_field = urlFalse
            with self.assertRaises(ValidationError):
                test_object.save()
