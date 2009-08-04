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
    def variations(self):
        for obj in self.values():
            if asm.cms.interfaces.IVariation.providedBy(obj):
                yield obj

    def getVariation(self, parameters, create=False):
        assert isinstance(parameters, VariationParameters)
        for var in self.variations:
            if var.parameters == parameters:
                return var
        if create:
            return self.addVariation(parameters)
        raise KeyError(parameters)

    def addVariation(self, parameters):
        variation = self.factory()
        variation.parameters = VariationParameters(parameters)
        self['-'.join(parameters)] = variation
        return variation

    @property
    def factory(self):
        return zope.component.getUtility(
            asm.cms.interfaces.IVariationFactory, name=self.type)


class Variation(grok.Model):

    zope.interface.implements(asm.cms.interfaces.IVariation)

    def __init__(self):
        super(Variation, self).__init__()
        self.parameters = BTrees.OOBTree.OOTreeSet()

    def variations(self):
        return self.__parent__.variations

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
def add_initial_variation(page, event):
    parameters = set()
    for factory in zope.component.getAllUtilitiesRegisteredFor(
            asm.cms.interfaces.IInitialVariationParameters):
        parameters.update(factory())
    page.addVariation(parameters)


class DeletePage(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def update(self):
        Page = self.context
        self.target = page.__parent__
        del page.__parent__[page.__name__]

    def render(self):
        self.redirect(self.url(self.target))


class DeleteVariation(grok.View):

    grok.context(Variation)

    def update(self):
        page = self.context.__parent__
        self.target = page
        del page[self.context.__name__]

    def render(self):
        self.redirect(self.url(self.target))


class Actions(grok.ViewletManager):
    grok.name('actions')
    grok.context(zope.interface.Interface)


class VariationActions(grok.Viewlet):

    grok.viewletmanager(Actions)
    grok.context(Variation)

class PageActions(grok.Viewlet):

    grok.viewletmanager(Actions)
    grok.context(Page)


class Variations(grok.ViewletManager):
    grok.name('variations')
    grok.context(zope.interface.Interface)


class PageVariations(grok.Viewlet):
    grok.viewletmanager(Variations)
    grok.context(zope.interface.Interface)
    grok.template('variations')


@grok.adapter(Variation, asm.cms.interfaces.IRetailSkin)
@grok.implementer(zope.traversing.browser.interfaces.IAbsoluteURL)
def variation_url(variation, request):
    return zope.component.getMultiAdapter(
        (variation.__parent__, request),
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
            (self.request,), asm.cms.interfaces.IVariationSelector):
            parameters.update(args)
        parameters = VariationParameters(parameters)
        try:
            return subpage.getVariation(parameters)
        except KeyError:
            return subpage


class VariationTraverse(grok.Traverser):

    grok.context(asm.cms.interfaces.IVariation)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def traverse(self, name):
        page = self.context.__parent__
        subpage = page.get(name)
        if not asm.cms.interfaces.IPage.providedBy(subpage):
            return
        parameters = set()
        for args in zope.component.subscribers(
            (self.request,), asm.cms.interfaces.IVariationSelector):
            parameters.update(args)
        parameters = VariationParameters(parameters)
        try:
            return subpage.getVariation(parameters)
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
            (self.request,), asm.cms.interfaces.IVariationSelector):
            parameters.update(args)
        parameters = VariationParameters(parameters)
        try:
            return page.getVariation(parameters)
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


class VariationParameters(object):
    """Variation parameters are immutable.

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

        return VariationParameters(parameters)
