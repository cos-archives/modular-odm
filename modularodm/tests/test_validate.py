import unittest
import datetime

# MODM imports

from modularodm import StoredObject

from modularodm.storage import PickleStorage

from modularodm.fields import(
    BooleanField,
    DateTimeField,
    FloatField,
    IntegerField,
    StringField,
)

from modularodm.validators import MinValueValidator, MaxValueValidator
from modularodm.validators import MinLengthValidator, MaxLengthValidator

from modularodm.validators import RegexValidator, URLValidator


# Describe a table
class TestSchema(StoredObject):

    _id = StringField(primary=True)

    # Simple fields

    intfield = IntegerField(list=False, validate=True)
    floatfield = FloatField(list=False, validate=True)
    boolfield = BooleanField(list=False, validate=True)
    datetimefield = DateTimeField(list=False, validate=True)
    stringfield = StringField(list=False, validate=True)
    regexfield = StringField(list=False, validate=RegexValidator('^foo$'))
    urlfield = StringField(list=False, validate=URLValidator())

    int_min_field = IntegerField(validate=MinValueValidator(3))
    int_max_field = IntegerField(validate=MaxValueValidator(15))
    string_min_field = StringField(validate=MinLengthValidator(3))
    string_max_field = StringField(validate=MaxLengthValidator(15))

    # List fields

    # int_list = IntegerField(list=True, validate=MinValueValidator(3))
    # float_list = FloatField(list=True, validate=True)
    # bool_list = BooleanField(list=True, validate=True)
    # datetime_list = DateTimeField(list=True, default=[])
    # string_list = StringField(list=True, validate=True)

    _meta = {'optimistic' : True}

# Tell the table to store data in a .pickle file

TestSchema.set_storage(PickleStorage('test_schema'))

def create_schema(schema_name, **fields):

    fields['_id'] = StringField(primary=True)
    fields['_meta'] = {'optimistic' : True}

    schema = type(
        schema_name,
        (StoredObject,),
        fields
    )

    schema.set_storage(PickleStorage(schema_name))

    return schema


class TestValidate(unittest.TestCase):

    def _clear_database(self):
        pass

    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    # Type-based validation

    def test_validate_string(self):
        '''
        Assert that the field cannot be saved with any type other than string
        '''
        bad_string_values = [
            datetime.datetime.now(),
            42,
            True,
        ]

        testrow = TestSchema()

        for bad_string_value in bad_string_values:
            testrow.stringfield = bad_string_value
            self.assertRaises(Exception, testrow.save)

    def test_validate_integer(self):
        '''
        Assert that the field cannot be saved with any type other than integer
        '''
        # helper_response = self.my_helper_function(...)
        bad_int_values = [
            5.1,
            'not a number',
            datetime.datetime.now(),
        ]

        testrow = TestSchema()

        for bad_int_value in bad_int_values:
            testrow.intfield = bad_int_value
            self.assertRaises(Exception, testrow.save)

    def test_validate_float(self):
        '''
        Assert that the field cannot be saved with any type other than float
        '''
        # this test revealed an error in the ODM
        # ints (e.g. 42) can't be stored in FloatField()s
        # probably not the desired behavior!
        bad_float_values = [
            'not a number',
            datetime.datetime.now(),
            42,
            True,
        ]

        testrow = TestSchema()

        for bad_float_value in bad_float_values:
            testrow.floatfield = bad_float_value
            self.assertRaises(Exception, testrow.save)

    def test_validate_boolean(self):
        '''
        Assert that the field cannot be saved with any type other than boolean
        '''
        bad_boolean_values = [
            'not a number',
            datetime.datetime.now(),
            42,
        ]

        testrow = TestSchema()

        for bad_boolean_value in bad_boolean_values:
            testrow.boolfield = bad_boolean_value
            self.assertRaises(Exception, testrow.save)

    # def test_validate_datetime(self):
    # '''
    # Assert that the field cannot be saved with any type other than datetime
    # '''
    #     # todo: address why it crashes on receiving a string
    #     bad_datetime_values = [
    #         'not a number',
    #         42,
    #         True,
    #     ]
    #
    #     testrow = TestSchema()
    #
    #     for bad_datetime_value in bad_datetime_values:
    #
    #         testrow.datetimefield = bad_datetime_value
    #         self.assertRaises(Exception, testrow.save)
    #
    # #Type-based validation for lists

    def test_validate_string_list(self):
        '''
        Assert that the field cannot be saved with lists containing any type other than string
        '''
        test_lists = [
            [1, 2, 3,],
            [4.0, 4.0,],
            [datetime.datetime.now(), datetime.datetime.now(),],
        ]

        Schema = create_schema(
            'string_list_schema',
            field=StringField(
                list=True,
                validate=True,
            )
        )

        test_row = Schema()
        for test_list in test_lists:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)


    def test_validate_integer_list(self):
        '''
        Assert that the field cannot be saved with lists containing any type other than integer
        '''
        test_lists = [
            [1.5,2.5,3.5],
            ['hey','hey',],
            [datetime.datetime.now(),datetime.datetime.now(),]
            ]

        Schema = create_schema(
            'integer_list_schema',
            field=IntegerField(
                list=True,
                validate=True,
            )
        )

        test_row = Schema()
        for test_list in test_lists:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)

    def test_validate_float_list(self):
        '''
        Assert that the field cannot be saved with lists containing any type other than float
        '''
        test_lists = [
            [1,2,3],
            ['hey','hey',],
            [datetime.datetime.now(),datetime.datetime.now(),]
            ]

        Schema = create_schema(
            'float_list_schema',
            field=FloatField(
                list=True,
                validate=True,
            )
        )

        test_row = Schema()
        for test_list in test_lists:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)

    def test_validate_boolean_list(self):
        '''
        Assert that the field cannot be saved with lists containing any type other than boolean
        '''
        test_lists = [
            [1,2,3],
            ['hey','hey',],
            [datetime.datetime.now(),datetime.datetime.now(),]
            ]

        Schema = create_schema(
            'bool_list_schema',
            field=BooleanField(
                list=True,
                validate=True,
            )
        )

        test_row = Schema()
        for test_list in test_lists:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)

    # this fails as the other datetime validation test does
    # def test_validate_datetime_list(self):
    #
    #     test_lists = [
    #         [1,2,3],
    #         ['hey','hey',],
    #         [True,False,]
    #         ]
    #
    #     testrow = TestSchema()
    #
    #     for test_list in test_lists:
    #         for test_item in test_list:
    #             testrow.datetimefield = test_item
    #             self.assertRaises(Exception, testrow.save)

    # Custom validators

    def test_validate_min_value(self):
        """
        Assert that an integer field with MinValueValidator(n) cannot
        be saved with a value less than n.
        """

        test_values = [
            -5,
            2,
        ]

        testrow = TestSchema()

        for value in test_values:
            testrow.int_min_field = value
            self.assertRaises(Exception, testrow.save)

    def test_validate_max_value(self):
        '''
        Assert that an integer field with MaxValueValidator(n) cannot
        be saved with a value greater than n.
        '''

        test_values = [
            300.8,
            700,
            900,
            101,
            'whoa',
        ]

        testrow = TestSchema()

        for value in test_values:
            testrow.int_max_field = value
            self.assertRaises(Exception, testrow.save)

    def test_validate_min_length(self):
        """
        Tests the minimum length validator for an individual StringField
        (with list=False).
        """

        test_strings = [
            'oa',
            'al',
            'v',
        ]

        testrow = TestSchema()

        for test_string in test_strings:
            testrow.string_min_field = test_string
            self.assertRaises(Exception, testrow.save)


    def test_validate_max_length(self):
        """
        Tests the maximum length validator for an individual StringField
        (with list=False).
        """
        test_strings = [
            'thisloooooooooooooooongstring',
            True,
            45,
        ]

        testrow = TestSchema()

        for test_string in test_strings:
            testrow.string_max_field = test_string
            self.assertRaises(Exception, testrow.save)

    def test_validate_regex(self):
        '''
        Assert that a string field with RegexValidator(str) cannot
        be saved with a value other than that specified by the regex
        '''

        test_strings = [
            2,
            4.5,
            'nope',
        ]

        testrow = TestSchema()

        for test_string in test_strings:
            testrow.regexfield = test_string
            self.assertRaises(Exception, testrow.save)

    def test_validate_url(self):
        '''
        Assert that a string field with RegexValidator(str) cannot
        be saved with a value other than that specified by the regex
        '''

        test_strings = [
            2,
            4.5,
            'nope',
            'www.thebomb.com'
        ]

        testrow = TestSchema()

        for test_string in test_strings:
            testrow.urlfield = test_string
            self.assertRaises(Exception, testrow.save)

    # def email_parser(self, email_parser):
    #     for character in email_list:

    # This test is written except for how to parse different email structures
    # def test_validate_email(self):
    #
    #     test_emails = [
    #         'melissa@centerforopenscience.org',
    #     ]
    #
    #     testrow = TestSchema()
    #
    #     for test_email in test_emails:
    #         testrow.stringfield = test_email
    #         stringcheck=self.string_check(test_email)
    #         self.assertTrue(stringcheck)
    #         email_list = test_email.split()
    #         self.assertTrue(email_parser)


    # Custom validators for lists

    def test_validate_min_value_list(self):
        '''
        Assert that a list with MinLengthValidator(n) cannot
        be saved with a value less than n.
        '''
        list_of_list_for_min = [
            ['whoa'],
            [2,4,0,],
            [2,3,4,5,],
            [2,3,4,5,6,7,8,9,11,12,],
        ]

        Schema = create_schema(
            'min_value_schema',
            field=IntegerField(
                list=True,
                validate=MinValueValidator(5),
                list_validate=[MinLengthValidator(5), MaxLengthValidator(7)]
            )
        )

        test_row = Schema()
        for test_list in list_of_list_for_min:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)


    def test_validate_max_value_list(self):
        '''
        Assert that a list with MaxLengthValidator(n) cannot
        be saved with a value greater than n.
        '''
        list_of_list_for_max = [
            ['whoa'],
            [2,4,40,],
            [2,3,4,5,],
            [2,3,4,5,6,7,8,9,11,12,],
        ]

        Schema = create_schema(
            'max_value_schema',
            field=IntegerField(
                list=True,
                validate=MaxValueValidator(15),
                list_validate=[MinLengthValidator(5), MaxLengthValidator(7)]
            )
        )
        test_row=Schema()
        for test_list in list_of_list_for_max:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)


    def test_validate_min_length_list(self):
        '''
        Assert that a list with MinLengthValidator(n) cannot
        be saved with a length less than n.
        '''
        list_of_items_for_min = [
            [1,2,3,4,5,],
            ['whoa','whoa',],
            ['awesome','awesome','awesome','awesome',],
            ['awesome','awesome','awesome','awesome','awesome','awesome','awesome','awesome',],
        ]

        Schema = create_schema(
            'min_length_schema',
            field=StringField(
                list=True,
                validate=MinLengthValidator(5),
                list_validate=[MinLengthValidator(5), MaxLengthValidator(7)]
            )
        )
        test_row=Schema()
        for test_list in list_of_items_for_min:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)

    def test_validate_max_length_list(self):
        '''
        Assert that a list with MaxLengthValidator(n) cannot
        be saved with a length greater than n.
        '''
        list_of_items_for_max = [
            [1,2,3,4,5,],
            ['whoaaaaa','whoaaaaa',],
            ['awesome','aweseome','awesome','awesome',],
            ['awesome','awesome','awesome','awesome','awesome','awesome','awesome','awesome',],
        ]

        Schema = create_schema(
            'max_length_schema',
            field=StringField(
                list=True,
                validate=MaxLengthValidator(7),
                list_validate=[MinLengthValidator(5), MaxLengthValidator(7)]
            )
        )
        # import pdb; pdb.set_trace()
        test_row=Schema()
        # for test_list in list_of_items_for_max:
        #     test_row.field = test_list
        #     self.assertRaises(Exception, test_row.save)

    # This test doesn't work because python cannot deepcopy regex
    # def test_validate_regex_list(self):
    #     list_of_regex = [
    #         [1,2,3,4,5,],
    #         ['foo','foo','foo','foo','foo','foo'],
    #         ['awesome','aweseome','awesome','awesome',],
    #         ['awesome','awesome','awesome','awesome','awesome','awesome','awesome','awesome',],
    #     ]
    #
    #     Schema = create_schema(
    #         'regex_list_schema',
    #         field=StringField(
    #             list=True,
    #             validate=RegexValidator('^foo$'),
    #             list_validate=[MinLengthValidator(5), MaxLengthValidator(7)]
    #         )
    #     )
    #     # import pdb; pdb.set_trace()
    #     test_row = Schema()
    #     for test_list in list_of_regex:
    #         test_row.field = test_list
    #         self.assertRaises(Exception, test_row.save)

    def test_validate_email_list(self):
        pass

    # Compound validators

    def test_min_and_max_value(self):
        '''
        Assert that a value with MinValueValidator(x) and
        MaxValueValidator(y) cannot
        be saved with a value less than x or
        a value greater than y
        '''
        test_values = [
            'whoa',
            2,
            52,
        ]

        testrow = TestSchema()

        for test_value in test_values:
            testrow.int_min_field = test_value
            testrow.int_max_field = test_value
            self.assertRaises(Exception, testrow.save)

    #Compound validators for lists

    def test_min_and_max_value_list(self):
        '''
        Assert that a list with MinLengthValidator(x) and
        MaxLengthValidator(y) cannot
        be saved with a length less than x or
        a length greater than y
        '''
        list_of_list_for_min_max = [
            ['whoa'],
            [2,4,0,],
            [17,],
            [5,5,5,5,],
            [5,5,5,5,6,7,8,9,11,12,],
        ]

        Schema = create_schema(
            'min_max_value_schema',
            field=IntegerField(
                list=True,
                validate=[MinValueValidator(5), MaxValueValidator(15)],
                list_validate=[MinLengthValidator(5), MaxLengthValidator(7)],
            )
        )
        test_row=Schema()
        for test_list in list_of_list_for_min_max:
            test_row.field = test_list
            self.assertRaises(Exception, test_row.save)

print '__name__', __name__
if __name__ == '__main__':
    unittest.main()