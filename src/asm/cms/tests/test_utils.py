# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.utils


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


def test_suite():
    return unittest.makeSuite(UtilityTests)
