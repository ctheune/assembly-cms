# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.page
import transaction
import unittest
import zope.app.component.hooks
import zope.intid.interfaces
import zope.component


class PageTests(asm.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(PageTests, self).setUp()
        self.cms['a'] = self.a = asm.cms.page.Page('htmlpage')
        self.cms['b'] = self.b = asm.cms.page.Page('htmlpage')
        transaction.commit()

    def test_b_inside_a(self):
        self.b.arrange(self.a, 'inside')
        self.failUnless('a' in self.b)
        self.failIf('a' in self.cms)

    def test_b_before_a(self):
        self.assertEquals(
            ['edition-', 'a', 'b'], list(self.cms))
        self.a.arrange(self.b, 'before')
        self.assertEquals(
            ['edition-', 'b', 'a'], list(self.cms))

    def test_a_after_b(self):
        self.assertEquals(
            ['edition-', 'a', 'b'], list(self.cms))
        self.b.arrange(self.a, 'after')
        self.assertEquals(
            ['edition-', 'b', 'a'], list(self.cms))
