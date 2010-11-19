# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.app.zopeappgenerations import getRootFolder
import ZODB.blob
import asm.cms.cms
import zope.app.component.hooks
import zope.intid.interfaces


# This generation registers CMS objects themselves with the intid utility.
def evolve(context):
    root = getRootFolder(context)
    for candidate in root.values():
        if not isinstance(candidate, asm.cms.cms.CMS):
            continue
        zope.app.component.hooks.setSite(candidate)
        try:
            stack = [candidate]
            while stack:
                obj = stack.pop()
                stack.extend(obj.subpages)
                if not obj.type == 'externalasset':
                    continue
                for edition in obj.editions:
                    gallery = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)
                    gallery.thumbnail = edition.thumbnail
                    edition.thumbnail = None
        finally:
            zope.app.component.hooks.setSite(None)
