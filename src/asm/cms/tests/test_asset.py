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
        self.assertEquals('image/x-png', asset.content_type)
