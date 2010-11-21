import asm.cms.cms
import asm.cms.testing
import asm.cms.typography
import grok
import unittest

class ParagraphTests(unittest.TestCase):
    def test_remove_empty_paragraph(self):
        self.assertEquals('', 
            asm.cms.typography.check_paragraphs('<p></p>'))

    def test_only_remove_empty_paragraph(self):
        self.assertEquals('<p>Assembly 2010</p>',
            asm.cms.typography.check_paragraphs('<p></p><p>Assembly 2010</p><p></p>'))

    def test_remove_whitespace_paragraph(self):
        self.assertEquals('',
            asm.cms.typography.check_paragraphs('<p>          </p>'))

    def test_remove_only_needed_whitespaces(self):
        self.assertEquals('<p>Assembly  2010</p>',
            asm.cms.typography.check_paragraphs('<p>            </p><p>Assembly  2010 </p><p>  </p>'))

    def test_remove_newline(self):
        self.assertEquals('',
            asm.cms.typography.check_paragraphs('<p>\n</p>'))

    def test_title_in_content(self):
        self.assertEquals('<p>Assembly on paras</p>',
            asm.cms.typography.title_in_content('Assembly 2010',
                '<H1>Assembly 2010</H1><p>Assembly on paras</p>'))

    def test_not_removing_parent(self):
        self.assertEquals('<p><img src="test" /></p>',
            ams.cms.typography.check_paragraphs('<p><img src="test" /></p>'))

