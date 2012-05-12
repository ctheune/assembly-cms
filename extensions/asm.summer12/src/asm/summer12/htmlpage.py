# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, PageContent, EmbeddedPageContent
from asm.cms.htmlpage import HTMLPage
from asm.cmsui.retail import Pagelet
from asm.cms.edition import select_edition, NullEdition
from asm.cms.asset import Asset
import grok


class Index(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(HTMLPage)
    grok.viewletmanager(PageContent)

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

    def _generate_gallery(self):
        for item in self.context.page.subpages:
            edition = select_edition(item, self.request)
            if not isinstance(edition, Asset):
                continue
            yield edition

    def _generate_subnavigation(self):
        container = self.context.page
        if not list(container.subpages):
            container = container.__parent__
        for item in container.subpages:
            edition = select_edition(item, self.request)
            if not isinstance(edition, HTMLPage):
                continue
            if edition.has_tag('hide-navigation'):
                continue
            yield edition

    def update(self):
        self.breadcrumbs = list(self._generate_breadcrumbs())
        self.subnavigation = list(self._generate_subnavigation())
        self.gallery = list(self._generate_gallery())


class Embedded(Index):
    grok.layer(ISkin)
    grok.context(HTMLPage)
    grok.viewletmanager(EmbeddedPageContent)
    grok.template('embedded')
