from asm.cms.patches import get_application_for_view
import asm.cms.testing
import asm.cms.utils
import datetime
import grok
import unittest
import zope.publisher.browser


class UtilityTests(unittest.TestCase):

    def test_rewrite_urls(self):
        self.assertEquals(
            '<a href="bar"/>\n  <img src="bar"/>',
            asm.cms.utils.rewrite_urls(
                '<a href="test"/><img src="test"/>',
                lambda x: 'bar'))

    def test_rewrite_urls_nochange(self):
        self.assertEquals(
            '<a href="test"/>\n  <img src="test"/>',
            asm.cms.utils.rewrite_urls(
                '<a href="test"/><img src="test"/>',
                lambda x: None))

    def test_rewrite_urls_empty_first(self):
        self.assertEquals(
            '<a href="test"/>\n  <img src="test"/>',
            asm.cms.utils.rewrite_urls(
                '<a href=""/><img src=""/>',
                lambda x: 'test'))

    def test_rewrite_urls_attribute_missing(self):
        self.assertEquals(
            '<a/>\n  <img/>',
            asm.cms.utils.rewrite_urls(
                '<a/><img/>',
                lambda x: 'test'))

    def test_normalize_name(self):
        self.assertEquals('asdf', asm.cms.utils.normalize_name('asdf'))
        self.assertEquals('asdf', asm.cms.utils.normalize_name('ASDF'))
        self.assertEquals('asdf-bsdf',
                          asm.cms.utils.normalize_name('asdf bsdf'))
        self.assertEquals('asdf-bsdf',
                          asm.cms.utils.normalize_name('asdf/bsdf'))
        self.assertEquals('asdf-bsdf',
                          asm.cms.utils.normalize_name('asdf#bsdf'))
        self.assertEquals('asdf-bsdf',
                          asm.cms.utils.normalize_name('asdf?bsdf'))
        self.assertEquals('asdf-bsdf',
                          asm.cms.utils.normalize_name(u'asdf\xfcbsdf'))


class ViewApplicationTests(unittest.TestCase):

    def setUp(self):

        class View(object):
            pass
        self.view = View()

        class Contained(object):
            __parent__ = None
        self.contained = Contained()
        self.application = grok.Application()

    def test_context_no_parent(self):
        self.view.context = self.contained
        self.assertRaises(
            ValueError, get_application_for_view, self.view)

    def test_context_is_app(self):
        self.view.context = self.application
        self.assertEquals(
            self.application, get_application_for_view(self.view))

    def test_context_parent_is_app(self):
        self.view.context = self.contained
        self.view.context.__parent__ = self.application
        self.assertEquals(
            self.application, get_application_for_view(self.view))


class ViewResolveURLsTests(asm.cms.testing.FunctionalTestCase):

    def test_resolve(self):
        request = zope.publisher.browser.TestRequest()
        view = grok.View(self.cms, request)
        r = lambda x: view.resolve_relative_urls(x, self.cms)

        self.assertEquals(
            '<a href="http://127.0.0.1/cms/"/>',
            r('<a href="."/>'))
        self.assertEquals(
            '<a href="http://127.0.0.1/cms/x/y"/>',
            r('<a href="x/y"/>'))
        self.assertEquals(
            '<a href="http://127.0.0.1/x/y"/>',
            r('<a href="../x/y"/>'))
        self.assertEquals(
            '<a href="/foo/bar"/>',
            r('<a href="/foo/bar"/>'))
        self.assertEquals(
            '<a href="http://asdf"/>',
            r('<a href="http://asdf"/>'))
        self.assertEquals(
            '<a href="ftp://asdf"/>',
            r('<a href="ftp://asdf"/>'))
        self.assertEquals(
            '<a href="https://asdf"/>',
            r('<a href="https://asdf"/>'))
        self.assertEquals(
            '<a href="mailto://asdf"/>',
            r('<a href="mailto://asdf"/>'))
        self.assertEquals(
            '<a href="irc://asdf"/>',
            r('<a href="irc://asdf"/>'))
        self.assertEquals(
            '<a href="?asdf"/>',
            r('<a href="?asdf"/>'))
        self.assertEquals(
            '<a href="#asdf"/>',
            r('<a href="#asdf"/>'))


class DatetimeToHttpConversionTests(unittest.TestCase):

    class CustomUtcOffset(datetime.tzinfo):
        def __init__(self, minutes):
            self._offset = datetime.timedelta(minutes=minutes)

        def utcoffset(self, dt):
            return self._offset

        def dst(self, dt):
            return datetime.timedelta(0)

    ZERO_UTC_OFFSET = CustomUtcOffset(0)

    def test_non_timezoned_time_fails(self):
        current_date = datetime.datetime(
            2000, 10, 10, 10, 10, 10)
        self.assertRaises(
            AssertionError,
            asm.cms.utils.datetime_to_http_timestamp,
            current_date)

    def test_tzinfo_not_in_utc(self):
        current_date = datetime.datetime(
            2000, 10, 10, 10, 10, 10, tzinfo=self.CustomUtcOffset(1))
        self.assertRaises(
            AssertionError,
            asm.cms.utils.datetime_to_http_timestamp,
            current_date)

    def test_valid_two_number_date(self):
        current_date = datetime.datetime(
            2000, 10, 10, 10, 10, 10, tzinfo=self.ZERO_UTC_OFFSET)
        self.assertEquals(
            asm.cms.utils.datetime_to_http_timestamp(current_date),
            'Tue, 10 Oct 2000 10:10:10 GMT')

    def test_valid_one_number_date(self):
        current_date = datetime.datetime(
            2000, 1, 1, 1, 1, 1, tzinfo=self.ZERO_UTC_OFFSET)
        self.assertEquals(
            asm.cms.utils.datetime_to_http_timestamp(current_date),
            'Sat, 1 Jan 2000 01:01:01 GMT')
