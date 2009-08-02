# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import zope.interface
import asm.cms.interfaces
import asm.cms.form
import megrok.pagelet


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

    def getVariation(self, parameters):
        for var in self.variations:
            if parameters == var.parameters:
                return var
        raise KeyError(parameters)


class Variation(grok.Model):

    zope.interface.implements(asm.cms.interfaces.IVariation)


class AddLocation(asm.cms.form.AddForm):

    grok.context(asm.cms.interfaces.ILocation)

    form_fields = grok.AutoFields(asm.cms.interfaces.ILocation)
    factory = Location

    def chooseName(self, obj):
        return obj.__name__


class AddVariation(grok.View):

    grok.context(asm.cms.interfaces.ILocation)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    def update(self, parameters):
        page = asm.cms.page.Page()
        page.parameters = set(parameters.split())
        self.context[parameters] = page

        session = zope.session.interfaces.ISession(self.request)
        session['asm.cms']['variation'] = parameters

    def render(self):
        self.redirect(self.url(self.context))


class Index(megrok.pagelet.Pagelet):

    grok.context(asm.cms.interfaces.ILocation)

    def __init__(self, context, request):
        super(Index, self).__init__(context, request)
        session = zope.session.interfaces.ISession(self.request)

        try:
            self.variation = context.getVariation(session['asm.cms']['variation'])
        except KeyError:
            self.variation = None

    def __call__(self):
        if self.variation:
            view = zope.component.getMultiAdapter((self.variation, self.request), name='index')
            self.render = view.__call__
        return super(Index, self).__call__()


class SelectVariation(grok.View):

    grok.context(zope.interface.Interface)

    def update(self, parameters):
        session = zope.session.interfaces.ISession(self.request)
        session['asm.cms']['variation'] = set(parameters.split(' '))

    def render(self):
        self.redirect(self.url(self.context))
