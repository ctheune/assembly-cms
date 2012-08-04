from zope.app.zopeappgenerations import getRootFolder
import asm.cms.cms
import zope.app.component.hooks
import zope.intid.interfaces


# This generation gets rid of modification dates that don't have tzinfo
def evolve(context):
    root = getRootFolder(context)
    for candidate in root.values():
        if not isinstance(candidate, asm.cms.cms.CMS):
            continue
        zope.app.component.hooks.setSite(candidate)
        intids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
        for edition in candidate.editions:
            intids.register(edition)
