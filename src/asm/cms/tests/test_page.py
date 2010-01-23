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
        self.root = self.getRootFolder()
        self.root['cms'] = asm.cms.cms.CMS()
        zope.app.component.hooks.setSite(self.root['cms'])
        self.root['cms']['a'] = asm.cms.page.Page('htmlpage')
        self.root['cms']['b'] = asm.cms.page.Page('htmlpage')
        self.a = self.root['cms']['a'].editions.next()
        self.b = self.root['cms']['b'].editions.next()
        transaction.commit()
        self.request = zope.publisher.browser.TestRequest()
        self.intids = zope.component.getUtility(
            zope.app.intid.interfaces.IIntIds)

    def test_b_inside_a(self):
        arrange = asm.cms.page.Arrange(self.b.page, self.request)
        arrange.update(self.intids.getId(self.a), 'inside')
        self.failUnless('a' in self.b.page)
        self.failIf('a' in self.root['cms'])

    def test_b_before_a(self):
        self.assertEquals(['edition-', 'a', 'b'],
                          list(self.root['cms']))
        arrange = asm.cms.page.Arrange(self.a.page, self.request)
        arrange.update(self.intids.getId(self.b), 'before')
        self.assertEquals(['edition-', 'b', 'a'],
                          list(self.root['cms']))

    def test_a_after_b(self):
        self.assertEquals(['edition-', 'a', 'b'],
                          list(self.root['cms']))
        arrange = asm.cms.page.Arrange(self.b.page, self.request)
        arrange.update(self.intids.getId(self.a), 'after')
        self.assertEquals(['edition-', 'b', 'a'],
                          list(self.root['cms']))
