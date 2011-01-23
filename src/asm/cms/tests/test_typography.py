import asm.cms.cms
import asm.cms.testing
import asm.cms.typography
import grok
import unittest


class ParagraphTests(unittest.TestCase):

    def setUp(self):
        self.page = asm.cms.htmlpage.HTMLPage()

    def clean(self):
        asm.cms.typography.clean_typography(self.page)
        return self.page.content

    def test_remove_empty_paragraph(self):
        self.page.content = '<p></p>'
        self.assertEquals('', self.clean())

    def test_only_remove_empty_paragraph(self):
        self.page.content = '<p></p><p>Assembly 2010</p><p></p>'
        self.assertEquals('<p>Assembly 2010</p>', self.clean())

    def test_remove_whitespace_paragraph(self):
        self.page.content = '<p>          </p>'
        self.assertEquals('', self.clean())

    def test_remove_newline(self):
        self.page.content = '<p>\n</p>'
        self.assertEquals('', self.clean())

    def test_title_in_content(self):
        self.page.title = 'Assembly 2010'
        self.page.content = '<H1>Assembly 2010</H1><p>Assembly on paras</p>'
        self.assertEquals('<p>Assembly on paras</p>', self.clean())

    def test_not_removing_parent(self):
        # Our output gets beautified so we end up with additional whitespace.
        self.page.content = '<p><img src="test" /></p>'
        self.assertEquals('<p>\n    <img src="test"/>\n  </p>', self.clean())
