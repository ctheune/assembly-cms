# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import zope.interface
import asm.cms.interfaces
import asm.cms.form
import megrok.pagelet
import BTrees.OOBTree


class Location(grok.Container):

    zope.interface.implements(asm.cms.interfaces.ILocation)

    @property
    def sublocations(self):
        for obj in self.values():
            if asm.cms.interfaces.ILocation.providedBy(obj):
                yield obj

    @property
    def variations(self):
        for obj in self.values():
            if asm.cms.interfaces.IVariation.providedBy(obj):
                yield obj

    def getVariation(self, parameters, create=False):
        for var in self.variations:
            if set(parameters) == set(var.parameters):
                return var
        if create:
            return self.addVariation(parameters)
        raise KeyError(parameters)

    def addVariation(self, parameters, variation=None):
        if variation is None:
            variation = self.factory()
        variation.parameters.update(parameters)
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


class AddLocation(asm.cms.form.AddForm):

    grok.context(asm.cms.interfaces.IVariation)

    form_fields = grok.AutoFields(asm.cms.interfaces.ILocation)
    factory = Location

    def chooseName(self, obj):
        return obj.__name__

    def add(self, obj):
        name = self.chooseName(obj)
        self.context.__parent__[name] = obj
        self.target = obj


@grok.subscribe(asm.cms.interfaces.ILocation, grok.IObjectAddedEvent)
def add_initial_variation(location, event):
    variation = location.factory()
    zope.event.notify(asm.cms.interfaces.InitialVariationCreated(variation))
    location.addVariation(variation.parameters, variation)


class SelectVariation(grok.View):

    grok.context(zope.interface.Interface)

    def update(self, parameters):
        session = zope.session.interfaces.ISession(self.request)
        session['asm.cms']['variation'] = set(parameters.split(' '))

    def render(self):
        self.redirect(self.url(self.context))


@zope.component.adapter(asm.cms.interfaces.ICMSSkin)
def select_cms_variation(request):
    session = zope.session.interfaces.ISession(request)
    return session['asm.cms'].get('variation', [])


class Actions(grok.ViewletManager):
    grok.name('actions')
    grok.context(zope.interface.Interface)


class Variations(grok.ViewletManager):
    grok.name('variations')
    grok.context(zope.interface.Interface)


class LocationVariations(grok.Viewlet):
    grok.viewletmanager(Variations)
    grok.context(zope.interface.Interface)
    grok.template('variations')


@grok.adapter(Variation, grok.IBrowserRequest)
@grok.implementer(zope.traversing.browser.interfaces.IAbsoluteURL)
def variation_url(variation, request):
    return zope.component.getMultiAdapter(
        (variation.__parent__, request),
        zope.traversing.browser.interfaces.IAbsoluteURL)


class VariationTraverse(grok.Traverser):

    grok.context(asm.cms.interfaces.IVariation)

    def traverse(self, name):
        obj = self.context.__parent__.get(name)
        if not asm.cms.interfaces.ILocation.providedBy(obj):
            return
        arguments = set()
        for args in zope.component.subscribers(
            (self.request,), asm.cms.interfaces.IVariationSelector):
            arguments.update(args)
        try:
            obj = obj.getVariation(arguments)
        except KeyError:
            pass
        return obj


class RootTraverse(grok.Traverser):

    grok.context(zope.app.folder.interfaces.IRootFolder)
    grok.layer(grok.IBrowserRequest)

    def traverse(self, name):
        obj = self.context.get(name)
        if not asm.cms.interfaces.ILocation.providedBy(obj):
            return
        arguments = set()
        for args in zope.component.subscribers(
            (self.request,), asm.cms.interfaces.IVariationSelector):
            arguments.update(args)
        try:
            obj = obj.getVariation(arguments)
        except KeyError:
            pass
        return obj


class RetailLocationIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    grok.context(asm.cms.interfaces.ILocation)
    grok.name('index')

    def render(self):
        return 'This page is not available.'


class CMSLocationIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.context(asm.cms.interfaces.ILocation)
    grok.name('index')

    def render(self):
        return ('This page is not available with the currently selected variation of %s' % 
                zope.session.interfaces.ISession(self.request)['asm.cms'].get('variation'))
