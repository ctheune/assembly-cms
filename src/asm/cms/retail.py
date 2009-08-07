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

    We also hide the editions' real URLs and point them to the pages' URLs.

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
        # XXX This code should probably refactored out of here.
        # We start out with all editions being acceptable.
        editions = dict((x, 0) for x in subpage.editions)
        for selector in zope.component.subscribers(
            (subpage, self.request,), asm.cms.interfaces.IEditionSelector):
            # Clean out all editions which are neither preferred nor accepted
            # by the current selector
            selected = set()
            selected.update(selector.preferred)
            selected.update(selector.acceptable)
            for edition in list(editions.keys()):
                if edition not in selected:
                    del editions[edition]

            for edition in selector.preferred:
                editions.setdefault(edition, 0)
                editions[edition] += 1
            for edition in selector.acceptable:
                editions.setdefault(edition, 0)

        if not editions:
            # XXX Put in NullEdition here?
            return subpage

        editions = editions.items()
        editions.sort(key=lambda x:x[1], reverse=True)
        return editions[0][0]

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
