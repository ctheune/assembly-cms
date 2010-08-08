# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.page
import transaction
import unittest
import zope.app.component.hooks
import zope.app.intid.interfaces
import zope.component


class PageTests(asm.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(PageTests, self).setUp()
        self.cms['a'] = asm.cms.page.Page('htmlpage')
        self.cms['b'] = asm.cms.page.Page('htmlpage')
        self.a = self.cms['a'].editions.next()
        self.b = self.cms['b'].editions.next()
        transaction.commit()
        self.request = zope.publisher.browser.TestRequest()
        self.intids = zope.component.getUtility(
            zope.app.intid.interfaces.IIntIds)

    def test_b_inside_a(self):
        arrange = asm.cms.page.Arrange(self.b.page, self.request)
        arrange.update(self.intids.getId(self.a.page), 'inside')
        self.failUnless('a' in self.b.page)
        self.failIf('a' in self.cms)

    def test_b_before_a(self):
        self.assertEquals(['edition-', 'a', 'b'],
                          list(self.cms))
        arrange = asm.cms.page.Arrange(self.a.page, self.request)
        arrange.update(self.intids.getId(self.b.page), 'before')
        self.assertEquals(['edition-', 'b', 'a'],
                          list(self.cms))

    def test_a_after_b(self):
        self.assertEquals(['edition-', 'a', 'b'],
                          list(self.cms))
        arrange = asm.cms.page.Arrange(self.b.page, self.request)
        arrange.update(self.intids.getId(self.a.page), 'after')
        self.assertEquals(['edition-', 'b', 'a'],
                          list(self.cms))
