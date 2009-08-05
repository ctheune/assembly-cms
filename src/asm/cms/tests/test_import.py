# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import unittest
from asm.cms.importer import fix_relative_links


class ImportTests(unittest.TestCase):

    def test_html_link_normalization(self):
        self.assertEquals(
            '<a href="asm/about">asdf</a>\n'
            '  <a href=".">bsdf</a>',
            fix_relative_links('<a href="/assembly09/asm/about">asdf</a>'
                               '<a href="/assembly09/">bsdf</a>',
                               '/assembly09'))


def test_suite():
    return unittest.makeSuite(ImportTests)
