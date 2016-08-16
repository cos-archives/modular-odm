# -*- coding: utf-8 -*-

from modularodm import StoredObject
from modularodm.exceptions import ValidationError
from modularodm.fields import StringField, IntegerField
from modularodm.validators import URLValidator

from tests.base import ModularOdmTestCase

class UrlValueValidatorTestCase(ModularOdmTestCase):

    def test_url(self):

        testsPositive = [u'http://Bücher.de', u'http://localhost:5000/meetings', u'http://foo.com/blah_blah',
                         u'http://foo.com/blah_blah/', u'http://foo.com/blah_blah_(wikipedia)',
                         u'http://userid:password@example.com:8080', u'http://userid:password@example.com:8080/',
                         u'http://userid@example.com', u'http://userid@example.com/', u'http://userid@example.com:8080',
                         u'http://userid@example.com:8080/', u'http://userid:password@example.com',
                         u'http://userid:password@example.com/', u'http://142.42.1.1', u'http://142.42.1.1/',
                         u'http://142.42.1.1:8080/',
                         u'http://➡.ws/䨹', u'http://⌘.ws', u'http://⌘.ws/', u'http://foo.com/blah_(wikipedia)#cite-1',
                         u'http://foo.com/blah_(wikipedia)_blah#cite-1', u'http://foo.com/unicode_(✪)_in_parens',
                         u'http://foo.com/(something)?after=parens', u'http://☺.damowmow.com/',
                         u'http://code.google.com/events/#&product=browser', u'http://j.mp', u'ftp://foo.bar/baz',
                         u'http://foo.bar/?q=Test%20URL-encoded%20stuff', u'http://مثال.إختبار', u'http://例子.测试',
                         u'http://उदाहरण.परीक्षा', u'http://-.~_!$&\'()*+,;=:%40:80%2f::::::@example.com',
                         u'http://1337.net', u'definitelyawebsite.com?real=yes&page=definitely',
                         u'http://a.b-c.de',
                         u'http://10.1.1.0', u'http://10.1.1.255', u'http://224.1.1.1', u'foo.com', ]

        testsNegative = [u'http://', u'http://.', u'http://..', u'http://../',
                         u'http://?', u'http://??', u'http://??/', u'http://#', u'http://##', u'http://##/',
                         u'http://foo.bar?q=Spaces should be encoded', u'//', u'//a', u'///a', u'///', u'http:///a',
                         u'rdar://1234', u'h://test', u'http:// shouldfail.com', u':// should fail',
                         u'http://foo.bar/foo(bar)baz quux', u'ftps://foo.bar/', u'http://-error-.invalid/',
                         u'http://1.1.1.1.1', u'http://-a.b.co',
                         u'http://3628126748', u'http://.www.foo.bar/', u'http://www.foo.bar./',
                         u'http://.www.foo.bar./']

        class Foo(StoredObject):
            _id = IntegerField()
            url_field = StringField(
                list=False,
                validate=[URLValidator()]
            )

        Foo.set_storage(self.make_storage())
        test_object = Foo()

        for urlTrue in testsPositive:
            test_object.url_field = urlTrue
            test_object.save()

        for urlFalse in testsNegative:
            test_object.url_field = urlFalse
            with self.assertRaises(ValidationError):
                test_object.save()
