# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import datetime
import grok
import zope.component
import zope.event
import zope.interface

STATE_PUBLIC = 'workflow:public'
STATE_DRAFT = 'workflow:draft'


def publish(draft, publication_date=None):
    if publication_date is None:
        publication_date = datetime.datetime.now()
    location = draft.__parent__

    public = set(draft.parameters)
    public.remove(STATE_DRAFT)
    public.add(STATE_PUBLIC)

    try:
        public = location.getVariation(public)
    except KeyError:
        public = location.addVariation(public)

    public.copyFrom(draft)
    public._workflow_publication_date = publication_date
    zope.event.notify(asm.workflow.interfaces.PublishedEvent(draft, public))


@grok.subscribe(asm.cms.interfaces.IInitialVariationCreated)
def set_draft_status(event):
    event.variation.parameters.insert(STATE_DRAFT)


@zope.component.adapter(asm.cms.interfaces.IRetailSkin)
def select_retail_variation(request):
    return set([STATE_PUBLIC])



class PublishMenuItem(grok.Viewlet):
    grok.viewletmanager(asm.cms.location.Actions)
    grok.context(asm.cms.interfaces.IVariation)


class Publish(grok.View):

    grok.context(asm.cms.interfaces.IVariation)

    def update(self):
        publish(self.context)
        self.flash(u"Published draft.")

    def render(self):
        self.redirect(self.url(self.context))


class Revert(grok.View):

    grok.context(asm.cms.interfaces.IVariation)

    def update(self):
        public = set(self.context.parameters)
        if STATE_DRAFT in public:
            public.remove(STATE_DRAFT)
        public.add(STATE_PUBLIC)

        draft = set(self.context.parameters)
        if STATE_PUBLIC in draft:
            draft.remove(STATE_PUBLIC)
        draft.add(STATE_DRAFT)

        location = self.context.__parent__
        try:
            public = location.getVariation(public)
        except KeyError:
            self.flash(u"Can not revert because no public version exists.")
            return
        try:
            draft = location.getVariation(draft)
        except KeyError:
            draft = location.addVariation(draft)
        draft.copyFrom(public)
        self.flash(u"Reverted to content from public version.")

    def render(self):
        self.redirect(self.url(self.context))
