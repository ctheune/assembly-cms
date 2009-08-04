# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.edition

EP = asm.cms.edition.EditionParameters


class EditionTests(unittest.TestCase):

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


def test_suite():
    return unittest.makeSuite(EditionTests)
