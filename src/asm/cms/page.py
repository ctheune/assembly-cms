# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import BTrees.OOBTree
import asm.cms.form
import asm.cms.interfaces
import grok
import megrok.pagelet
import re
import zope.app.form.browser.source
import zope.interface


class Page(grok.Container):

    zope.interface.implements(asm.cms.interfaces.IPage)

    @property
    def subpages(self):
        for obj in self.values():
            if asm.cms.interfaces.IPage.providedBy(obj):
                yield obj

    @property
    def editions(self):
        for obj in self.values():
            if asm.cms.interfaces.IEdition.providedBy(obj):
                yield obj

    def getEdition(self, parameters, create=False):
        assert isinstance(parameters, EditionParameters)
        for var in self.editions:
            if var.parameters == parameters:
                return var
        if create:
            return self.addEdition(parameters)
        raise KeyError(parameters)

    def addEdition(self, parameters):
        edition = self.factory()
        edition.parameters = EditionParameters(parameters)
        self['-'.join(parameters)] = edition
        return edition

    @property
    def factory(self):
        return zope.component.getUtility(
            asm.cms.interfaces.IEditionFactory, name=self.type)


class Edition(grok.Model):

    zope.interface.implements(asm.cms.interfaces.IEdition)

    def __init__(self):
        super(Edition, self).__init__()
        self.parameters = BTrees.OOBTree.OOTreeSet()

    def editions(self):
        return self.__parent__.editions

    @property
    def page(self):
        return self.__parent__


class AddPage(asm.cms.form.AddForm):

    grok.context(asm.cms.interfaces.IPage)

    form_fields = grok.AutoFields(asm.cms.interfaces.IPage)
    form_fields['type'].custom_widget = (
        lambda field, request: zope.app.form.browser.source.SourceRadioWidget(
                field, field.source, request))

    factory = Page

    def chooseName(self, obj):
        return obj.__name__

    def add(self, obj):
        name = self.chooseName(obj)
        self.context[name] = obj
        self.target = obj


@grok.subscribe(asm.cms.interfaces.IPage, grok.IObjectAddedEvent)
def add_initial_edition(page, event):
    parameters = set()
    for factory in zope.component.getAllUtilitiesRegisteredFor(
            asm.cms.interfaces.IInitialEditionParameters):
        parameters.update(factory())
    page.addEdition(parameters)


class DeletePage(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def update(self):
        Page = self.context
        self.target = page.__parent__
        del page.__parent__[page.__name__]

    def render(self):
        self.redirect(self.url(self.target))


class DeleteEdition(grok.View):

    grok.context(Edition)

    def update(self):
        page = self.context.__parent__
        self.target = page
        del page[self.context.__name__]

    def render(self):
        self.redirect(self.url(self.target))


class Actions(grok.ViewletManager):
    grok.name('actions')
    grok.context(zope.interface.Interface)


class EditionActions(grok.Viewlet):

    grok.viewletmanager(Actions)
    grok.context(Edition)

class PageActions(grok.Viewlet):

    grok.viewletmanager(Actions)
    grok.context(Page)


class Editions(grok.ViewletManager):
    grok.name('editions')
    grok.context(zope.interface.Interface)


class PageEditions(grok.Viewlet):
    grok.viewletmanager(Editions)
    grok.context(zope.interface.Interface)
    grok.template('editions')


@grok.adapter(Edition, asm.cms.interfaces.IRetailSkin)
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
        parameters = EditionParameters(parameters)
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
        parameters = EditionParameters(parameters)
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
        parameters = EditionParameters(parameters)
        try:
            return page.getEdition(parameters)
        except KeyError:
            return page


class RetailPageIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    grok.context(asm.cms.interfaces.IPage)
    grok.name('index')

    def render(self):
        self.request.response.setStatus(404)
        return 'This page is not available.'


class CMSPageIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.context(asm.cms.interfaces.IPage)
    grok.name('index')
    grok.template('index')


class EditionParameters(object):
    """Edition parameters are immutable.

    All operations return a mutated copy of the parameters.

    """

    def __init__(self, initial=()):
        self.parameters = set(initial)

    def __eq__(self, other):
        return self.parameters == other.parameters

    def __iter__(self):
        return iter(self.parameters)

    def replace(self, old, new):
        """Replace a (possibly) existing parameter with a new one.

        If the old parameter doesn't exist it will be ignored, the new will be
        added in any case.

        The old parameter can be given with a globbing symbol (*) to match
        multiple parameters to replace at once.

        """
        parameters = set()
        parameters.add(new)

        remove = '^%s$' % old.replace('*', '.*')
        remove = re.compile(old)
        for p in self.parameters:
            if remove.match(p):
                continue
            parameters.add(p)

        return EditionParameters(parameters)
