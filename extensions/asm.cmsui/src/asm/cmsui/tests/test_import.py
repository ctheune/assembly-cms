# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

from asm.cms.htmlpage import fix_relative_links
import asm.cms.importer
import asm.cms.testing
import os.path
import unittest
import zope.publisher.browser


class ImportUnit(unittest.TestCase):

    def test_html_link_normalization(self):
        self.assertEquals(
            '<a href="asm/about">asdf</a>\n'
            '  <a href=".">bsdf</a>',
            fix_relative_links('<a href="/assembly09/asm/about">asdf</a>'
                               '<a href="/assembly09/">bsdf</a>',
                               '/assembly09'))


class ImportFunctional(asm.cms.testing.FunctionalTestCase):

    def test_import(self):
        request = zope.publisher.browser.TestRequest()
        importer = asm.cms.importer.Import(self.cms, request)
        importer.do_import(
            open(os.path.join(os.path.dirname(__file__),
                              'import.xml')).read())
        self.assertEquals(2, len(list(self.cms.subpages)))
        self.assertEquals('htmlpage', self.cms['testpage'].type)
        self.assertEquals('asset', self.cms['testimage'].type)


class ImportSelenium(asm.cms.testing.SeleniumTestCase):

    def test_import_form_available(self):
        s = self.selenium
        s.click('css=#actions .toggle-navigation')
        s.click("xpath=//h3[contains(text(),'Tools')]/following-sibling::div[@class='opener']")
        s.assertVisible("xpath=//button[contains(text(), 'Import content')]")
        s.clickAndWait("xpath=//button[contains(text(), 'Import content')]")
