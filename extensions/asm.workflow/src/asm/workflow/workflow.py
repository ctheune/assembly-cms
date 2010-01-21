# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import datetime
import grok
import pytz
import zope.component
import zope.event


WORKFLOW_PUBLIC = 'workflow:public'
WORKFLOW_DRAFT = 'workflow:draft'

WORKFLOW_LABELS = {WORKFLOW_PUBLIC: 'Public',
                   WORKFLOW_DRAFT: 'Draft'}


class Prefixes(object):

    zope.interface.implements(asm.cms.interfaces.IExtensionPrefixes)

    prefixes = set(['workflow'])


def publish(draft, publication_date=None):
    public = draft.parameters.replace(WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
    public = draft.page.getEdition(public, create=True)
    public.copyFrom(draft)
    public.modified = (
        publication_date or datetime.datetime.now(tz=pytz.UTC))
    zope.event.notify(asm.workflow.interfaces.PublishedEvent(draft, public))
    del draft.__parent__[draft.__name__]
    return public


def select_initial_parameters():
    return set([WORKFLOW_DRAFT])


class CMSEditionSelector(object):

    zope.interface.implements(asm.cms.IEditionSelector)
    zope.component.adapts(asm.cms.IPage, asm.cms.ICMSSkin)

    def __init__(self, page, request):
        self.preferred = []
        self.acceptable = []
        for edition in page.editions:
            if WORKFLOW_PUBLIC in edition.parameters:
                self.preferred.append(edition)
            else:
                self.acceptable.append(edition)


class RetailEditionSelector(object):

    zope.interface.implements(asm.cms.IEditionSelector)
    zope.component.adapts(
        asm.cms.IPage,
        asm.cms.interfaces.IRetailSkin)

    acceptable = ()

    def __init__(self, page, request):
        self.preferred = []
        for edition in page.editions:
            if WORKFLOW_PUBLIC in edition.parameters:
                self.preferred.append(edition)


class PublishMenuItem(grok.Viewlet):
    grok.viewletmanager(asm.cms.PageActionGroups)
    grok.context(asm.cms.IEdition)

    def current_version(self):
        for candidate in self.context.parameters:
            if candidate.startswith('workflow:'):
                return WORKFLOW_LABELS[candidate]

    def hints(self):
        hints = ''
        public_p = self.context.parameters.replace(
            'workflow:*', WORKFLOW_PUBLIC)
        try:
            public = self.context.page.getEdition(public_p)
        except KeyError:
            hints += 'No public version available. '
        else:
            draft = self.context.page.getEdition(
                public_p.replace('workflow:*', WORKFLOW_DRAFT), create=True)

            if draft is self.context:
                hints += 'Public version available. '

            if draft.modified > public.modified:
                hints + 'Draft is newer.'

        return hints

    def list_versions(self):
        for status in [WORKFLOW_DRAFT, WORKFLOW_PUBLIC]:
            p = self.context.parameters.replace('workflow:*', status)
            version = {}
            version['class'] = ''
            version['label'] = WORKFLOW_LABELS[status]
            try:
                version['edition'] = self.context.page.getEdition(p)
            except KeyError:
                continue

            if version['edition'] is self.context:
                version['class'] = 'selected'

            yield version


class Publish(asm.cms.ActionView):

    grok.context(asm.cms.IEdition)

    def update(self):
        self.context = publish(self.context)
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
        public = self.context.parameters.replace(
            WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
        try:
            public = page.getEdition(public)
        except KeyError:
            self.flash(u"Can not revert because no public edition exists.")
            return

        draft = public.parameters.replace(WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
        draft = page.getEdition(draft, create=True)
        draft.copyFrom(public)
        self.flash(u"Reverted draft changes.")
