# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.app.zopeappgenerations import getRootFolder
import ZODB.blob
import asm.cms.cms
import zope.app.component.hooks
import zope.intid.interfaces


# This generation converts asset strings into blobs.
def evolve(context):
    root = getRootFolder(context)
    for candidate in root.values():
        if not isinstance(candidate, asm.cms.cms.CMS):
            continue
        zope.app.component.hooks.setSite(candidate)
        try:
            for edition in asm.cms.edition.find_editions(
                    candidate, schema=asm.cms.interfaces.IAsset):
                if isinstance(edition.content, ZODB.blob.Blob):
                    continue
                if edition.content is None:
                    continue
                old = edition.content
                edition.content = ZODB.blob.Blob()
                f = edition.content.open('w')
                f.write(old)
        finally:
            zope.app.component.hooks.setSite(None)
