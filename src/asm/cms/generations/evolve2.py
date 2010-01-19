# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.app.zopeappgenerations import getRootFolder
import asm.cms.cms
import pytz


# This generation gets rid of modification dates that don't have tzinfo
def evolve(context):
    root = getRootFolder(context)
    for candidate in root.values():
        if not isinstance(candidate, asm.cms.cms.CMS):
            continue

        stack = [candidate]
        while stack:
            obj = stack.pop()
            stack.extend(obj.subpages)
            for edition in obj.editions:
                if edition.modified.tzinfo is None:
                    edition.modified = edition.modified.replace(
                        tzinfo=pytz.UTC)
