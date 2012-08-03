# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt


from zope.app.zopeappgenerations import getRootFolder
import asm.cms.cms
import asm.cms.interfaces
import asm.cms.search
import zc.catalog.catalogindex
import zope.app.component.hooks
import zope.catalog.interfaces
import zope.component


# This generation installs the new tag index.
def evolve(context):
    root = getRootFolder(context)
    for cms in root.values():
        if not isinstance(cms, asm.cms.cms.CMS):
            continue
        zope.app.component.hooks.setSite(cms)
        try:
            catalog = zope.component.getUtility(
                zope.catalog.interfaces.ICatalog, name='edition_catalog')
            catalog['tags'] = zc.catalog.catalogindex.SetIndex(
                    field_name='tags_set',
                    interface=asm.cms.interfaces.IEdition)
            catalog.updateIndexes()
        finally:
            zope.app.component.hooks.setSite(None)
