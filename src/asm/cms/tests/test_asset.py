# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

import asm.cms.asset


class AssetTests(unittest.TestCase):

    def test_constructor(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals('', asset.content)

    def test_size(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals(0, asset.size)
        asset.content = '.' * 100
        self.assertEquals(100, asset.size)


def test_suite():
    return unittest.makeSuite(AssetTests)
