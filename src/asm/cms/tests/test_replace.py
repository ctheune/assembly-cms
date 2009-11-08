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

    def test_find_occurences_content(self):
        self.page.content = u'fooasdfbar'
        occurences = list(self.replace.search('asdf'))
        self.assertEqual(1, len(occurences))

    def test_find_occurences_title(self):
        self.page.title = u'fooasdfbar'
        occurences = list(self.replace.search('asdf'))
        self.assertEqual(1, len(occurences))

    def test_find_occurences_title_and_content(self):
        self.page.title = u'fooasdfbar'
        self.page.content = u'fooasdfbar'
        occurences = list(self.replace.search('asdf'))
        self.assertEqual(2, len(occurences))

    def test_replace_occurence_content(self):
        self.page.content = u'fooasdfbar'
        occurence = self.replace.search('asdf').next()
        occurence.replace('lingonberry')
        self.assertEquals('foolingonberrybar', self.page.content)

    def test_replace_occurence_title(self):
        self.page.title = u'fooasdfbar'
        occurence = self.replace.search('asdf').next()
        occurence.replace('lingonberry')
        self.assertEquals('foolingonberrybar', self.page.title)

    def test_replace_occurence_title_and_content(self):
        self.page.title = u'fooasdfbar'
        self.page.content = u'fooasdfbar'
        for i, o in enumerate(self.replace.search('asdf')):
            o.replace('lingonberry%s' % i)
        self.assertEquals('foolingonberry0bar', self.page.title)
        self.assertEquals('foolingonberry1bar', self.page.content)

    def test_replace_multiple_occurences_straight(self):
        self.page.content = u'fooasdfbarasdfbaz'
        o1, o2 = self.replace.search('asdf')
        o1.replace('lingonberry')
        o2.replace('pancake')
        self.assertEquals(u'foolingonberrybarpancakebaz',
                          self.page.content)

    def test_replace_multiple_occurences_different_order(self):
        self.page.content = u'fooasdfbarasdfbaz'
        o1, o2 = self.replace.search('asdf')
        o2.replace('lingonberry')
        o1.replace('pancake')
        self.assertEquals(u'foopancakebarlingonberrybaz',
                          self.page.content)


def test_suite():
    return unittest.makeSuite(TestReplace)
