# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cms.htmlpage
import asm.cms.replace
import asm.cms.testing
import transaction
import unittest


class TestReplace(asm.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(TestReplace, self).setUp()
        self.cms['page'] = self.page = asm.cms.htmlpage.HTMLPage()
        self.replace = asm.cms.replace.HTMLReplace(self.page)

    def test_find_no_occurrences(self):
        occurrences = list(self.replace.search('asdf'))
        self.assertEqual([], occurrences)

    def test_find_occurrences_content(self):
        self.page.content = u'fooasdfbar'
        occurrences = list(self.replace.search('asdf'))
        self.assertEqual(1, len(occurrences))

    def test_find_occurrences_title(self):
        self.page.title = u'fooasdfbar'
        occurrences = list(self.replace.search('asdf'))
        self.assertEqual(1, len(occurrences))

    def test_find_occurrences_title_and_content(self):
        self.page.title = u'fooasdfbar'
        self.page.content = u'fooasdfbar'
        occurrences = list(self.replace.search('asdf'))
        self.assertEqual(2, len(occurrences))

    def test_replace_occurence_content(self):
        self.page.content = u'fooasdfbar'
        occurence, = self.replace.search('asdf')
        occurence.replace('lingonberry')
        self.assertEquals('foolingonberrybar', self.page.content)

    def test_replace_occurence_title(self):
        self.page.title = u'fooasdfbar'
        occurence, = self.replace.search('asdf')
        occurence.replace('lingonberry')
        self.assertEquals('foolingonberrybar', self.page.title)

    def test_replace_occurence_title_and_content(self):
        self.page.title = u'fooasdfbar'
        self.page.content = u'fooasdfbar'
        for i, o in enumerate(self.replace.search('asdf')):
            o.replace('lingonberry%s' % i)
        self.assertEquals('foolingonberry0bar', self.page.title)
        self.assertEquals('foolingonberry1bar', self.page.content)

    def test_replace_multiple_occurrences_straight(self):
        self.page.content = u'fooasdfbarasdfbaz'
        o1, o2 = self.replace.search('asdf')
        o1.replace('lingonberry')
        o2.replace('pancake')
        self.assertEquals(u'foolingonberrybarpancakebaz',
                          self.page.content)

    def test_replace_multiple_occurrences_different_order(self):
        self.page.content = u'fooasdfbarasdfbaz'
        o1, o2 = self.replace.search('asdf')
        o2.replace('lingonberry')
        o1.replace('pancake')
        self.assertEquals(u'foopancakebarlingonberrybaz',
                          self.page.content)

    def test_replace_multiple_occurrences_multiple_attributes(self):
        self.page.title = u'fooasdfbarasdfbaz'
        self.page.content = u'fooasdfbarasdfbaz'
        o1, o2, o3, o4 = self.replace.search('asdf')
        o1.replace('lingonberry')
        o2.replace('pancake')
        o3.replace('syrup')
        o4.replace('maple')
        self.assertEquals(u'foolingonberrybarpancakebaz',
                          self.page.title)
        self.assertEquals(u'foosyrupbarmaplebaz',
                          self.page.content)

    def test_replace_multiple_attributes_occurrences_different_order(self):
        self.page.title = u'fooasdfbarasdfbaz'
        self.page.content = u'fooasdfbarasdfbaz'
        o1, o2, o3, o4 = self.replace.search('asdf')
        o3.replace('syrup')
        o1.replace('lingonberry')
        o4.replace('maple')
        o2.replace('pancake')
        self.assertEquals(u'foolingonberrybarpancakebaz',
                          self.page.title)
        self.assertEquals(u'foosyrupbarmaplebaz',
                          self.page.content)

    def test_preview(self):
        self.page.content = u"""The object providing the existing interface is
        passed to the Adapter in <br/> the constructor, and is stored in an
        attribute named context. The source code for the grok.Adapter base
        class is simply:"""
        o1, = self.replace.search('constructor')
        self.assertEquals(u'ace is\n        '
                          'passed to the Adapter in &lt;br/&gt; the '
                          '<span class="match">constructor</span>, and '
                          'is stored in an\n        attribute named cont',
                          o1.preview)
