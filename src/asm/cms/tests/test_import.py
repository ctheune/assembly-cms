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
        data = open(os.path.join(os.path.dirname(__file__), 'import.xml'))
        importer = asm.cms.importer.Importer(self.cms, data)
        importer()
        self.assertEquals(2, len(list(self.cms.subpages)))
        self.assertEquals('htmlpage', self.cms['testpage'].type)
        self.assertEquals('asset', self.cms['testimage'].type)
