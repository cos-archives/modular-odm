import mock

from modularodm import StoredObject, fields, storage
from modularodm.translators import DefaultTranslator


def make_mock_storage():
    mock_storage = mock.create_autospec(storage.Storage)()
    mock_storage.translator = DefaultTranslator()
    return mock_storage


def make_model():
    class Model(StoredObject):
        _id = fields.IntegerField(primary=True)
        value = fields.StringField()
    Model.set_storage(make_mock_storage())
    return Model

