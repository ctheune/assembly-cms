# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.traversing.api
import zope.app.component.hooks
import transaction

zope.app.component.hooks.setSite(root['summer10'])

stack = [root['summer10']]
while stack:
    page = stack.pop()
    for draft in page.editions:
        if 'workflow:draft' not in draft.parameters:
            continue
        try:
            public = page.getEdition(
                draft.parameters.replace('workflow:draft', 'workflow:public'))
        except KeyError:
            # Don't delete if there's only a draft
            continue
        if draft == public:
            print zope.traversing.api.getPath(draft)
            del draft.__parent__[draft.__name__]
    stack.extend(page.subpages)
transaction.commit()
