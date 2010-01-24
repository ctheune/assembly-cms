

from zope.app.zopeappgenerations import getRootFolder
import asm.cms.cms


# Install generation and fixer for ensuring that every public version has a
# draft.


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
                if not 'workflow:public' in edition.parameters:
                    continue
                draft_p = edition.parameters.replace('workflow:public', 'workflow:draft')
                try:
                    draft = obj.getEdition(draft_p)
                except KeyError:
                    print "creating draft for", obj.__name__
                    draft = obj.getEdition(draft_p, create=True)
                    draft.copyFrom(edition)
