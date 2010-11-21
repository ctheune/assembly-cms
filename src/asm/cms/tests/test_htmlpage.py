# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

import asm.cms.htmlpage


class HTMLPageTests(unittest.TestCase):

    def test_constructor(self):
        htmlpage = asm.cms.htmlpage.HTMLPage()
        self.assertEquals('', htmlpage.content)

