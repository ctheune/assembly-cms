# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.interface


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    megrok.pagelet.template('templates/layout.pt')


class Navtree(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)


class ActionView(grok.View):
    grok.baseclass()
    grok.layer(asm.cms.interfaces.ICMSSkin)

    def render(self):
        self.redirect(self.url(self.context))


class Actions(grok.ViewletManager):
    grok.name('actions')
    grok.context(zope.interface.Interface)


@grok.adapter(asm.cms.interfaces.IEdition, asm.cms.interfaces.IRetailSkin)
@grok.implementer(zope.traversing.browser.interfaces.IAbsoluteURL)
def edition_url(edition, request):
    return zope.component.getMultiAdapter(
        (edition.__parent__, request),
        zope.traversing.browser.interfaces.IAbsoluteURL)


class PageTraverse(grok.Traverser):

    grok.context(asm.cms.interfaces.IPage)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def traverse(self, name):
        page = self.context
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


class EditionTraverse(grok.Traverser):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def traverse(self, name):
        page = self.context.__parent__
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


class RootTraverse(grok.Traverser):

    grok.context(zope.app.folder.interfaces.IRootFolder)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def traverse(self, name):
        page = self.context.get(name)
        if not asm.cms.interfaces.IPage.providedBy(page):
            return
        parameters = set()
        for args in zope.component.subscribers(
            (self.request,), asm.cms.interfaces.IEditionSelector):
            parameters.update(args)
        parameters = asm.cms.edition.EditionParameters(parameters)
        try:
            return page.getEdition(parameters)
        except KeyError:
            return page
