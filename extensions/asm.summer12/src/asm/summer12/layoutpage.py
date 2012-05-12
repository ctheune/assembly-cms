# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, PageContent
from asm.layoutpage.layoutpage import LayoutPage
import grok
import zope.component


class Index(grok.Viewlet):
    grok.context(LayoutPage)
    grok.viewletmanager(PageContent)
    grok.layer(ISkin)

    def render(self):
        return self.context.render(self.request, self.render_sub)

    def render_sub(self, request, obj):
        provider = zope.component.getMultiAdapter(
                (obj, request, self.view),
                zope.contentprovider.interfaces.IContentProvider,
                name='embedded-page-content')
        provider.update()
        return provider.render()
