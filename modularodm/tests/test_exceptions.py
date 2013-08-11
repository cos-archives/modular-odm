
import unittest

class TestExceptions(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multiple_primary_keys(self):
        """ Schema definition with multiple primary keys should throw an exception. """
        pass

    def test_must_be_loaded(self):
        """ Assigning an object that has not been saved as a foreign field should throw an exception. """
        pass

    def test_must_be_loaded_list(self):
        """ Assigning an object that has not been saved to a foreign list field should throw an exception. """
        pass

    def test_has_storage(self):
        """ Calling save on an object without an attached storage should throw an exception. """
        pass

    def test_storage_type(self):
        """ Assigning a non-Storage object in set_storage should throw an exception. """
        pass

    def test_validator_is_valid(self):
        """  """
        pass