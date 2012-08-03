# Copyright (c) 2009-2011 Assembly Organizing
# See also LICENSE.txt

from asm.cms.htmlpage import fix_relative_links
import asm.cms.importer
import asm.cms.testing
import os.path
import unittest
import zope.component


class ImportUnit(unittest.TestCase):

    def test_html_link_normalization(self):
        self.assertEquals(
            '<a href="asm/about">asdf</a>\n'
            '  <a href=".">bsdf</a>',
            fix_relative_links('<a href="/assembly09/asm/about">asdf</a>'
                               '<a href="/assembly09/">bsdf</a>',
                               '/assembly09'))


def test_handler(event):
    test_handler.results.append(event)


class ImportFunctional(asm.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(ImportFunctional, self).setUp()
        zope.component.provideHandler(
            test_handler, [asm.cms.interfaces.IContentImported])
        test_handler.results = []

    def test_import(self):
        data = open(os.path.join(os.path.dirname(__file__), 'import.xml'))
        importer = asm.cms.importer.Importer(self.cms, data.read())
        importer()
        self.assertEquals(2, len(list(self.cms.subpages)))
        self.assertEquals('htmlpage', self.cms['testpage'].type)
        self.assertEquals('asset', self.cms['testimage'].type)
        self.assertEquals([], test_handler.results[0].errors)
        self.assertEquals(self.cms, test_handler.results[0].site)
