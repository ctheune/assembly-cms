# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.asset
import os.path
import unittest


class AssetTests(unittest.TestCase):

    def test_constructor(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals('', asset.content)

    def test_size(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals(0, asset.size)
        asset.content = '.' * 100
        self.assertEquals(100, asset.size)

    def test_magic(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals('data', asset.content_type)
        asset.content = open(
            os.path.join(os.path.dirname(__file__), '..',
                         'static', 'icons', 'pencil.png')).read()
        self.assertEquals('image/x-png', asset.content_type)


def test_suite():
    return unittest.makeSuite(AssetTests)
