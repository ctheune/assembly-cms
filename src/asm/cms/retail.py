# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.interface


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    megrok.pagelet.template('templates/retail.pt')


class Page(megrok.pagelet.Pagelet):

    grok.baseclass()
    grok.layer(asm.cms.interfaces.IRetailSkin)


class RetailTraverser(grok.Traverser):
    """Retail traversers try to map URLs to page *editions* when the URL would
    normally point to a page.

    They also hide the editions' real URLs and point them to the pages' URLs.

    """

    grok.baseclass()

    # This directive is currently ignored due to LP #408819. See workaround
    # below.
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def traverse(self, name):
        if not asm.cms.interfaces.IRetailSkin.providedBy(self.request):
            # Workaround for grok.layer bug
            return
        page = self.get_context()
        subpage = page.get(name)
        if not asm.cms.interfaces.IPage.providedBy(subpage):
            return
        parameters = set()
        for args in zope.component.subscribers(
            (self.request,), asm.cms.interfaces.IEditionSelector):
            parameters.update(args)
        parameters = asm.cms.edition.EditionParameters(parameters)
        try:
            return subpage.getEdition(parameters)
        except KeyError:
            return subpage

    def get_context(self):
        return self.context


class RootTraverse(RetailTraverser):

    grok.context(zope.app.folder.interfaces.IRootFolder)


class PageTraverse(RetailTraverser):

    grok.context(asm.cms.interfaces.IPage)


class EditionTraverse(RetailTraverser):

    grok.context(asm.cms.interfaces.IEdition)

    def get_context(self):
        return self.context.page
