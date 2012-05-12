import unittest
from asm.layoutpage.layoutpage import LayoutTemplate


class LayoutTemplateTests(unittest.TestCase):

    def test_pattern_with_empty_string_returns_empty_set(self):
        self.assertEquals(
            [],
            LayoutTemplate.MARKER_PATTERN.findall(''))

    def test_pattern_returns_correct_name(self):
        self.assertEquals(
            ['test'],
            LayoutTemplate.MARKER_PATTERN.findall('${test}'))

    def test_find_markers_with_multiple_markers(self):
        self.assertEquals(
            ['test', 'test2'],
            LayoutTemplate.MARKER_PATTERN.findall('${test}  ${test2}'))

    def test_find_markers_with_recurring_markers(self):
        self.assertEquals(
            ['test', 'test'],
            LayoutTemplate.MARKER_PATTERN.findall('${test}  ${test}'))

    def test_replace_full_stack(self):
        results = {'': 'empty', 'test': 'nonempty'}
        template = LayoutTemplate('${} ${test} ${}', results.get)
        self.assertEquals('empty nonempty empty', template())
