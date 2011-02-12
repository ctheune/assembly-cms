# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.traversing.api

stack = [root['summer10']]

while stack:
    page = stack.pop()
    for edition in page.editions:
        for tag in edition.parameters:
            if not ':' in tag:
                print zope.traversing.api.getPath(edition)
    stack.extend(page.subpages)
