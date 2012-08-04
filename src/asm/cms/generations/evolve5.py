from zope.app.zopeappgenerations import getRootFolder
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
            intids = zope.component.getUtility(zope.intid.IIntIds)
            intids.register(candidate)
        finally:
            zope.app.component.hooks.setSite(None)
