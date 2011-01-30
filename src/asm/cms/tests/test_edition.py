# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import minimock
import unittest
import asm.cms.edition
import zope.component

EP = asm.cms.edition.EditionParameters


class EditionTests(unittest.TestCase):

    def setUp(self):
        self.tracker = minimock.TraceTracker()

    def tearDown(self):
        minimock.restore()
        del self.tracker

    def test_parameters_empty(self):
        self.assertEquals(
            set(),
            EP().parameters)

    def test_parameters_init(self):
        self.assertEquals(
            set(['asdf']),
            EP(['asdf']).parameters)

    def test_parameters_compare_empty(self):
        p1 = EP()
        p2 = EP()
        self.assertEquals(p1, p2)

    def test_parameters_compare_nonempty(self):
        p1 = EP([1])
        p2 = EP([2])
        self.assertNotEquals(p1, p2)

        p1_1 = EP([1])
        self.assertEquals(p1, p1_1)

    def test_parameters_iter(self):
        p = EP([1,2,3])
        self.assertEquals(set([1,2,3]), set(p))

    def test_parameters_replace_simple(self):
        self.assertEquals(
            EP([1]), EP().replace('foo', 1))
        self.assertEquals(
            EP([1]), EP(['foo']).replace('foo', 1))

    def test_parameters_replace_glob(self):
        self.assertEquals(
            EP(['lang:fi']),
            EP(['lang:en', 'lang:de']).replace('lang:*', 'lang:fi'))

    def test_edition_compares_equal_to_self(self):
        edition = asm.cms.edition.Edition()
        self.assertEquals(edition, edition)

    def test_edition_with_same_content_is_equal(self):
        edition1 = asm.cms.edition.Edition()
        edition2 = asm.cms.edition.Edition()
        self.assertEquals(edition1, edition2)

    def test_edition_with_different_content_is_unequal(self):
        edition1 = asm.cms.edition.Edition()
        edition2 = asm.cms.edition.Edition()
        edition2.title = u'Huah'
        self.assertNotEquals(edition1, edition2)

    def test_select_2_editions_with_same_content_selected_by_identity(self):
        # We once hit a bad issue where we used a comparison in
        # `select_edition` that was based on identity. However, due to the
        # fact that we have a special implementation of __eq__ we need to 
        # ensure that we select based on identity rather than equality.
        # This test isn't bullet proof, but it keeps us from making the
        # exactly same mistake again.
        page = minimock.Mock('page')
        ed1 = asm.cms.edition.Edition()
        ed2 = asm.cms.edition.Edition()
        page.editions = [ed1, ed2]
        selector = minimock.Mock('selector')
        selector.preferred = [ed1]
        selector.acceptable = []
        minimock.mock('zope.component.subscribers', returns=[selector],
                      tracker=self.tracker)
        self.assertTrue(ed1 is asm.cms.edition.select_edition(page, None))
        selector.preferred = [ed2]
        self.assertTrue(ed2 is asm.cms.edition.select_edition(page, None))
