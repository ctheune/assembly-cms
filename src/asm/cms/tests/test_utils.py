# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cms.utils
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

class ParagraphTests(unittest.TestCase):
    def test_remove_empty_paragraph(self):
        self.assertEquals('', 
            asm.cms.utils.check_paragraphs('<p></p>'))

    def test_only_remove_empty_paragraph(self):
        self.assertEquals('<p>Assembly 2010</p>',
            asm.cms.utils.check_paragraphs('<p></p><p>Assembly 2010</p><p></p>'))

    def test_remove_whitespace_paragraph(self):
        self.assertEquals('',
            asm.cms.utils.check_paragraphs('<p>          </p>'))

    def test_remove_only_needed_whitespaces(self):
        self.assertEquals('<p>Assembly  2010</p>',
            asm.cms.utils.check_paragraphs('<p>            </p><p>Assembly  2010 </p><p>  </p>'))

    def test_remove_newline(self):
        self.assertEquals('',
            asm.cms.utils.check_paragraphs('<p>\n</p>'))

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
            ValueError, asm.cms.get_application_for_view, self.view)

    def test_context_is_app(self):
        self.view.context = self.application
        self.assertEquals(
            self.application, asm.cms.get_application_for_view(self.view))

    def test_context_parent_is_app(self):
        self.view.context = self.contained
        self.view.context.__parent__ = self.application
        self.assertEquals(
            self.application, asm.cms.get_application_for_view(self.view))


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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilityTests))
    suite.addTest(unittest.makeSuite(ViewApplicationTests))
    suite.addTest(unittest.makeSuite(ViewResolveURLsTests))
    suite.addTest(unittest.makeSuite(ParagraphTests))
    return suite
