from asm.reviewlist.reviewlist import install_utility
from zope.app.zopeappgenerations import getRootFolder
import asm.cms.cms
import zope.app.component.hooks


# This generation installs the new tag index.
def evolve(context):
    root = getRootFolder(context)
    for cms in root.values():
        if not isinstance(cms, asm.cms.cms.CMS):
            continue
        zope.app.component.hooks.setSite(cms)
        try:
            install_utility(cms)
        except KeyError:
            pass
        finally:
            zope.app.component.hooks.setSite(None)
