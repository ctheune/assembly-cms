# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.page
import asm.cms.testing
import transaction
import unittest


class CMSUI(asm.cms.testing.SeleniumTestCase):

    def test_cms_redirects_to_editor(self):
        self.selenium.open('http://mgr:mgrpw@%s/++skin++cms/cms' %
                           self.selenium.server)
        self.assertEquals(
            u'http://localhost:8087/++skin++cms/cms/edition-/@@edit',
            self.selenium.getLocation())

    def test_switch_to_navigation_and_back(self):
        s = self.selenium
        s.assertNotVisible("css=#navigation")
        s.assertVisible("css=#content")

        s.click('css=#actions .toggle-navigation')
        s.assertVisible("css=#navigation")
        s.assertNotVisible("css=#content")

        s.click('css=#navigation-actions .toggle-navigation')
        s.assertNotVisible("css=#navigation")
        s.assertVisible("css=#content")

    def test_breadcrumbs(self):
        # We need to add a sub-page as the root never shows up in the
        # breadcrumbs
        self.cms['xy'] = asm.cms.page.Page('htmlpage')
        self.cms['xy'].editions.next().title = u'A test page'
        transaction.commit()
        s = self.selenium
        s.open(
            'http://mgr:mgrpw@%s/++skin++cms/cms/xy/edition-/@@edit' %
            s.server)
        s.assertVisible(
            'xpath=//div[contains(@class, "breadcrumbs")]/'
            'a[contains(text(), "A test page")]')
        s.clickAndWait(
            'xpath=//div[contains(@class, "breadcrumbs")]/'
            'a[contains(text(), "A test page")]')
        s.assertElementPresent('name=form.actions.save')

    def test_additional_form_fields(self):
        s = self.selenium
        s.assertVisible('//h3[contains(text(), "Tags")]')
        s.assertNotVisible('name=form.tags')
        s.click('//h3[contains(text(), "Tags")]')
        s.assertVisible('name=form.tags')
