# Copyright (c) 2009-2010 Assembly Organizing
# See also LICENSE.txt

import ZODB.blob
import asm.cms.edition
import asm.cms.interfaces
import grok
import magic
import zope.interface


class Asset(asm.cms.edition.Edition):
    """An asset stores binary data, like images.

    This can be used to storage images to display in the web site or binary
    files to download from the site.

    It is expected that custom logic can be used in the future that builds on
    the mime type of the content.

    """

    zope.interface.implements(asm.cms.interfaces.IAsset)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'File/Image'
    factory_order = 2
    factory_visible = True

    content = None

    def copyFrom(self, other):
        super(Asset, self).copyFrom(other)
        self.content = other.content
        self.title = other.title

    def __eq__(self, other):
        if not super(Asset, self).__eq__(other):
            return False
        return self.content == other.content

    @property
    def size(self):
        if self.content is None:
            return 0
        f = self.content.open('r')
        f.seek(0, 2)
        size = f.tell()
        f.close()
        return size

    @property
    def content_type(self):
        if self.content is None:
            return None
        return magic.whatis(self.content.open('r').read())
