# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.htmlpage
import asm.cms.replace


class TestReplace(unittest.TestCase):

    def setUp(self):
        self.page = asm.cms.htmlpage.HTMLPage()
        self.replace = asm.cms.replace.Replace(self.page)

    def test_find_no_occurences(self):
        occurences = list(self.replace.search('asdf'))
        self.assertEqual([], occurences)

    def test_find_occurences_body(self):
        self.page.content = u'fooasdfbar'
        occurences = list(self.replace.search('asdf'))
        self.assertEqual(1, len(occurences))

    def test_find_occurences_title(self):
        self.page.title = u'fooasdfbar'
        occurences = list(self.replace.search('asdf'))
        self.assertEqual(1, len(occurences))

    def test_find_occurences_title_and_body(self):
        self.page.title = u'fooasdfbar'
        self.page.content = u'fooasdfbar'
        occurences = list(self.replace.search('asdf'))
        self.assertEqual(2, len(occurences))

    def test_replace_occurence_body(self):
        self.page.content = u'fooasdfbar'
        occurence = self.replace.search('asdf').next()
        occurence.replace('lingonberry')
        self.assertEquals('foolingonberrybar', self.page.content)

    def test_replace_occurence_title(self):
        self.page.title = u'fooasdfbar'
        occurence = self.replace.search('asdf').next()
        occurence.replace('lingonberry')
        self.assertEquals('foolingonberrybar', self.page.title)


def test_suite():
    return unittest.makeSuite(TestReplace)
