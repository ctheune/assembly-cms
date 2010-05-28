# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.page
import asm.cms.testing
import grok
import transaction
import unittest
import zope.event


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

    def test_search_no_results(self):
        s = self.selenium
        s.type('name=q', 'asdf')
        s.selenium.key_press('name=q', r'\13')
        s.waitForPageToLoad()
        s.waitForTextPresent(
            'The search for "asdf" returned\n no results.')

    def test_search_result_preview_htmlpage(self):
        self.cms.editions.next().content = 'sometext asdf someothertext'
        zope.event.notify(grok.ObjectModifiedEvent(self.cms.editions.next()))
        transaction.commit()
        s = self.selenium
        s.type('name=q', 'asdf')
        s.selenium.key_press('name=q', r'\13')
        s.waitForPageToLoad()
        s.assertTextPresent('sometext asdf someothertext')
        s.assertElementPresent('//span[@class="match"]')

    def test_change_page_type(self):
        s = self.selenium
        s.assertNotVisible('xpath=//input[@value="Change page type"]')
        s.click('//h3[contains(text(), "Page")]')
        s.assertVisible('xpath=//input[@value="Change page type"]')
        s.clickAndWait('xpath=//input[@value="Change page type"]')
        s.click('id=form.type.0') # News section
        s.clickAndWait('name=form.actions.change')
        self.assertEquals(
            'http://localhost:8087/++skin++cms/cms/edition-/@@edit',
            s.getLocation())
        transaction.begin()
        self.assertEquals('news', self.cms.type)

    def test_delete_page(self):
        s = self.selenium
        self.cms['xy'] = asm.cms.page.Page('htmlpage')
        edition = self.cms['xy'].editions.next()
        edition.title = u'A test page'
        intids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
        xy_id = intids.getId(edition)
        transaction.commit()
        s.open(
            'http://mgr:mgrpw@%s/++skin++cms/cms/xy/edition-/@@edit' %
            s.server)
        s.click('css=#actions .toggle-navigation')
        s.waitForElementPresent('css=#%s a' % xy_id)
        s.clickAndWait('css=#delete-page')
        self.assertEquals(u'Delete page "\xa0A test page"?',
                          s.selenium.get_confirmation())
        s.assertText('css=li.message', 'Page deleted.')
        transaction.abort()
        self.assertRaises(KeyError, self.cms.__getitem__, 'xy')

    def test_cant_delete_root(self):
        intids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
        edition = self.cms.editions.next()
        edition.title = u'Foobar'
        transaction.commit()
        cms_id = intids.getId(edition)
        s = self.selenium
        s.refresh()
        s.waitForPageToLoad()
        s.click('css=#actions .toggle-navigation')
        s.waitForElementPresent('css=#%s a' % cms_id)
        s.clickAndWait('css=#delete-page')
        self.assertEquals(u'Delete page "\xa0Foobar"?',
                          s.selenium.get_confirmation())
        s.assertText('css=li.warning', 'Cannot delete the root page!')
        transaction.abort()
        # Ensure the CMS is really still there.
        self.assert_(self.getRootFolder()['cms'])
