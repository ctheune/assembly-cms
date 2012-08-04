from zope.app.zopeappgenerations import getRootFolder
import asm.cms.cms
import zope.app.component.hooks
import zope.intid.interfaces


# This generation updates the text indexes because they changed the way
# `documentCount` works.
def evolve(context):
    root = getRootFolder(context)
    for cms in root.values():
        if not isinstance(cms, asm.cms.cms.CMS):
            continue
        zope.app.component.hooks.setSite(cms)
        try:
            catalog = zope.component.getUtility(
                zope.catalog.interfaces.ICatalog, name='edition_catalog')
            catalog['body'].clear()
            catalog.updateIndexes()
        finally:
            zope.app.component.hooks.setSite(None)
