# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.asset
import os.path
import unittest
import ZODB.blob


class AssetTests(unittest.TestCase):

    def test_constructor(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals(None, asset.content)

    def test_copy(self):
        asset1 = asm.cms.asset.Asset()
        asset1.title = 'asdf'
        asset1.content = 'foo'
        asset2 = asm.cms.asset.Asset()
        asset2.copyFrom(asset1)
        self.assertEquals('asdf', asset2.title)
        self.assertEquals('foo', asset2.content)

    def test_compare(self):
        asset1 = asm.cms.asset.Asset()
        asset1.title = 'asdf'
        asset1.content = 'foo'
        self.assertEquals(asset1, asset1)

        asset2 = asm.cms.asset.Asset()
        asset2.title = 'bsdf'
        self.assertNotEquals(asset1, asset2)

        asset2.title = 'asdf'
        asset2.content = 'foo'

        self.assertEquals(asset1, asset2)

    def test_size(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals(0, asset.size)
        asset.content = ZODB.blob.Blob()
        asset.content.open('w').write('.' * 100)
        self.assertEquals(100, asset.size)

    def test_magic(self):
        asset = asm.cms.asset.Asset()
        self.assertEquals(None, asset.content_type)
        b = asset.content = ZODB.blob.Blob()
        f = b.open('w')
        f.write(open(os.path.join(os.path.dirname(__file__), 'pencil.png')
                     ).read())
        f.close()
        self.assertEquals('image/png', asset.content_type)
