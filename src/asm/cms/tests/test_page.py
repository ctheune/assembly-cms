# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.page
import asm.cms.edition


class EditionTests(unittest.TestCase):

    def test_updateOrder(self):
        page = asm.cms.page.Page()
        page['a'] = asm.cms.page.Page()
        page['b'] = asm.cms.page.Page()
        page['c'] = asm.cms.page.Page()
        page['edition'] = edition = asm.cms.edition.Edition()
        # The initial order is `as created`.
        self.assertEquals(['a', 'b', 'c', 'edition'],
                          page.keys())
        update = asm.cms.edition.UpdateOrder(edition, None)

        # We order by stating a new order, all items left out are appended at
        # the end.
        update.update(['c', 'b', 'a'])
        self.assertEquals(['c', 'b', 'a', 'edition'],
                          page.keys())


def test_suite():
    return unittest.makeSuite(EditionTests)
