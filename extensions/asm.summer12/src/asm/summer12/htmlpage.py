# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, EmbeddedPageContent, Breadcrumbs
from asm.cms.htmlpage import HTMLPage
import grok


class Embedded(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(HTMLPage)
    grok.viewletmanager(EmbeddedPageContent)
    grok.template('embedded')

class Breadcrumbs(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(HTMLPage)
    grok.viewletmanager(Breadcrumbs)

    def _generate_breadcrumbs(self):
        candidate = self.context.page
        while True:
            candidate = candidate.__parent__
            if candidate is self.view.application:
                return
            edition = select_edition(candidate, self.request)
            if isinstance(edition, NullEdition):
                continue
            yield edition

    def update(self):
        self.breadcrumbs = reversed(list(self._generate_breadcrumbs()))
