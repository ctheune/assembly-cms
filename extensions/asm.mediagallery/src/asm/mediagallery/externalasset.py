# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.mediagallery.interfaces
import grok
import persistent
import zope.interface
import zope.app.form.browser.objectwidget


class ExternalAsset(asm.cms.edition.Edition):

    zope.interface.implements(asm.mediagallery.interfaces.IExternalAsset)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'External asset'

    locations = ()

    def copyFrom(self, other):
        super(ExternalAsset, self).copyFrom(other)
        # XXX deepcopy
        self.locations = other.locations

    def __eq__(self, other):
        if not super(ExternalAsset, self).__eq__(other):
            return False
        return (self.locations == other.locations)


def setupObjectInputWidget(field, request):
    factory = zope.component.getUtility(zope.component.interfaces.IFactory,
                                        name=field.schema.__name__)
    return zope.app.form.browser.objectwidget.ObjectWidget(field, request, factory)


class Edit(asm.cms.form.EditionEditForm):

    grok.context(ExternalAsset)

    main_fields = grok.AutoFields(ExternalAsset).select(
        'title', 'locations')


class ViewGallery(asm.cms.Pagelet):

    grok.context(ExternalAsset)

    def update(self):
        return self.redirect(self.url(self.context))

    def render(self):
        return self.url(self.context)


class Index(asm.cms.Pagelet):

    grok.context(ExternalAsset)

    def embed(self):
        for service_choice in self.context.locations:
            try:
                service = zope.component.getUtility(
                    asm.mediagallery.interfaces.IEmbeddableContentHostingService,
                    name=service_choice.service_id)
            except LookupError:
                pass
            else:
                return service.embed_code(service_choice.id)

    def links(self, include=None, exclude=None, max=None):
        count = 0
        for service_choice in self.context.locations:
            if include and service_choice.service_id not in include:
                continue
            if exclude and service_choice.service_id in exclude:
                continue
            service = zope.component.getUtility(
                asm.mediagallery.interfaces.IContentHostingService,
                name=service_choice.service_id)
            yield service.link_code(service_choice.id)
            count += 1
            if count == max:
                return



class HostingServiceChoice(persistent.Persistent):

    zope.interface.implements(
        asm.mediagallery.interfaces.IHostingServiceChoice)
