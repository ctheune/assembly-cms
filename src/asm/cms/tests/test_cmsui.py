# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.testing
import unittest


class CMSUI(asm.cms.testing.SeleniumTestCase):

    def test_cms_redirects_to_editor(self):
        s = self.selenium
        s.open('http://mgr:mgrpw@%s/++skin++cms/cms' % s.server)
        self.assertEquals(
            u'http://localhost:8087/++skin++cms/cms/edition-/@@edit',
            s.getLocation())

    def test_switch_to_navigation_and_back(self):
        s = self.selenium
        s.open('http://mgr:mgrpw@%s/++skin++cms/cms' % s.server)
        s.assertNotVisible("css=#navigation")
        s.assertVisible("css=#content")

        s.click('css=#actions .toggle-navigation')
        s.assertVisible("css=#navigation")
        s.assertNotVisible("css=#content")

        s.click('css=#navigation-actions .toggle-navigation')
        s.assertNotVisible("css=#navigation")
        s.assertVisible("css=#content")
