# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.utils
import grok


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
            ValueError, asm.cms.application, self.view)

    def test_context_is_app(self):
        self.view.context = self.application
        self.assertEquals(
            self.application, asm.cms.application(self.view))

    def test_context_parent_is_app(self):
        self.view.context = self.contained
        self.view.context.__parent__ = self.application
        self.assertEquals(
            self.application, asm.cms.application(self.view))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilityTests))
    suite.addTest(unittest.makeSuite(ViewApplicationTests))
    return suite
