# -*- coding: utf-8 -*-
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields

def test_subclass():
    """Test that fields are inherited from superclasses.

    """
    class ParentSchema(StoredObject):
        _id = fields.StringField()
        parent_field = fields.StringField()

    class ChildSchema(ParentSchema):
        pass

    assert_in('parent_field', ParentSchema._fields)
    assert_in('parent_field', ChildSchema._fields)
