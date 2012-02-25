# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, NavigationBar
import grok
import zope.interface
from asm.cms.edition import select_edition, NullEdition


class ToplevelNavigation(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)
    grok.viewletmanager(NavigationBar)

    def items(self):
        root = self.view.application

        for item in root.subpages:
            edition = select_edition(item, self.request)
            if isinstance(edition, NullEdition):
                continue
            if edition.has_tag('hide-navigation'):
                continue
            yield edition


class Localnav(grok.View):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)

    def items(self):
        return map(lambda p:asm.cms.edition.select_edition(p, self.request),
                   self.context.page.subpages)
