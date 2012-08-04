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

    @property
    def current_section(self):
        root = self.view.application

        context = self.context
        while context != self.view.application:
            context = context.__parent__
            if context in root.subpages:
                return select_edition(context, self.request)
        return None


class Localnav(grok.View):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)

    def items(self):
        return map(lambda p: select_edition(p, self.request),
                   self.context.page.subpages)
