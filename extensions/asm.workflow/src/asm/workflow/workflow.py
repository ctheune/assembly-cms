# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import datetime
import grok
import zope.component
import zope.event


WORKFLOW_PUBLIC = 'workflow:public'
WORKFLOW_DRAFT = 'workflow:draft'


def publish(draft, publication_date=None):
    public = draft.parameters.replace(WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
    public = draft.page.getEdition(public, create=True)
    public.copyFrom(draft)
    # XXX Sticking the publication date on a protected arg is icky
    public._workflow_publication_date = (
        publication_date or datetime.datetime.now())
    zope.event.notify(asm.workflow.interfaces.PublishedEvent(draft, public))


def select_initial_parameters():
    return set([WORKFLOW_DRAFT])


@zope.component.adapter(asm.cms.interfaces.IRetailSkin)
def select_retail_edition(request):
    return set([WORKFLOW_PUBLIC])


class PublishMenuItem(grok.Viewlet):
    grok.viewletmanager(asm.cms.Actions)
    grok.context(asm.cms.IEdition)


class Publish(asm.cms.ActionView):

    grok.context(asm.cms.IEdition)

    def update(self):
        publish(self.context)
        self.flash(u"Published draft.")


class Revert(asm.cms.ActionView):
    """Revert a draft's changes by copying the current state of the published
    edition.

    This action view can be applied either on the draft or the public copy with
    the same result.

    """

    grok.context(asm.cms.IEdition)

    def update(self):
        page = self.context.page
        public = self.context.parameters.replace(WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
        try:
            public = page.getEdition(public)
        except KeyError:
            self.flash(u"Can not revert because no public edition exists.")
            return

        draft = public.parameters.replace(WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
        draft = page.getEdition(draft, create=True)
        draft.copyFrom(public)
        self.flash(u"Reverted draft changes.")
