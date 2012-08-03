# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cmsui.base
import asm.cmsui.interfaces
import datetime
import grok
import pytz
import zope.component
import zope.event


WORKFLOW_PUBLIC = 'workflow:public'
WORKFLOW_DRAFT = 'workflow:draft'

WORKFLOW_LABELS = {WORKFLOW_PUBLIC: 'Public',
                   WORKFLOW_DRAFT: 'Draft'}


class WorkflowLabels(grok.GlobalUtility):

    zope.interface.implements(asm.cms.interfaces.IEditionLabels)
    grok.name('workflow')

    def lookup(self, tag):
        return WORKFLOW_LABELS[tag]


class Prefixes(object):

    zope.interface.implements(asm.cms.interfaces.IExtensionPrefixes)

    prefixes = set(['workflow'])


def publish(current_edition, publication_date=None):
    draft = current_edition.parameters.replace(WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
    draft = current_edition.page.getEdition(draft)
    public = draft.parameters.replace(WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
    public = draft.page.getEdition(public, create=True)
    public.copyFrom(draft)
    public.modified = (
        publication_date or datetime.datetime.now(tz=pytz.UTC))
    zope.event.notify(asm.workflow.interfaces.PublishedEvent(draft, public))
    # And now remove the draft after publication.
    del draft.__parent__[draft.__name__]
    return public


def select_initial_parameters(page):
    if page.type == 'asset':
        return set([WORKFLOW_PUBLIC])
    return set([WORKFLOW_DRAFT])


class CMSEditionSelector(object):

    zope.interface.implements(asm.cms.IEditionSelector)
    zope.component.adapts(asm.cmsui.interfaces.ICMSSkin)

    def __init__(self, request):
        pass

    def select(self, page):
        preferred = []
        acceptable = []
        for edition in page.editions:
            target = acceptable
            if WORKFLOW_DRAFT in edition.parameters:
                target = preferred
            elif WORKFLOW_PUBLIC in edition.parameters:
                # If it's public and there is no draft, then the public
                # version is preferred, otherwise if there is a draft, it's
                # just acceptable. This allows promotion of a public version
                # from another plugin.
                try:
                    draft = page.getEdition(edition.parameters.replace(
                        'workflow:*', WORKFLOW_DRAFT))
                except KeyError:
                    target = preferred
            target.append(edition)
        return preferred, acceptable


class RetailEditionSelector(object):

    zope.interface.implements(asm.cms.IEditionSelector)
    zope.component.adapts(asm.cmsui.interfaces.IRetailBaseSkin)

    def __init__(self, request):
        pass

    def select(self, page):
        acceptable = []
        preferred = []
        for edition in page.editions:
            if WORKFLOW_PUBLIC in edition.parameters:
                preferred.append(edition)
        return preferred, acceptable


class PublishMenuItem(grok.Viewlet):
    grok.viewletmanager(asm.cmsui.base.PageActionGroups)
    grok.context(asm.cms.IEdition)

    def current_version(self):
        for candidate in self.context.parameters:
            if candidate.startswith('workflow:'):
                return WORKFLOW_LABELS[candidate]

    def is_draft(self):
        return WORKFLOW_DRAFT in self.context.parameters

    def is_public(self):
        return WORKFLOW_PUBLIC in self.context.parameters

    def has_draft(self):
        try:
            draft = self.context.parameters.replace(
                'workflow:*', WORKFLOW_DRAFT)
            self.context.page.getEdition(draft)
        except KeyError:
            return False
        return True

    def has_public(self):
        try:
            draft = self.context.parameters.replace(
                'workflow:*', WORKFLOW_PUBLIC)
            self.context.page.getEdition(draft)
        except KeyError:
            return False
        return True

    def hints(self):
        hints = ''
        public_p = self.context.parameters.replace(
            'workflow:*', WORKFLOW_PUBLIC)
        try:
            public = self.context.page.getEdition(public_p)
        except KeyError:
            hints += 'No public version available. '
        else:
            try:
                draft = self.context.page.getEdition(
                    public_p.replace('workflow:*', WORKFLOW_DRAFT))
            except KeyError:
                pass
            else:
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


class Publish(asm.cmsui.base.ActionView):

    grok.context(asm.cms.IEdition)

    def update(self):
        self.context = publish(self.context)
        self.redirect(self.url(self.context, '@@edit'))
        self.flash(u"Published draft.")


class DeletePublic(asm.cmsui.base.ActionView):

    grok.context(asm.cms.IEdition)
    grok.name('delete-public')

    def update(self):
        page = self.context.page
        public = self.context.parameters.replace(
            WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
        try:
            public = page.getEdition(public)
        except KeyError:
            self.flash(u"No public version to delete.")
            return

        draft = self.context.parameters.replace(
            WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
        try:
            draft = page.getEdition(draft)
        except KeyError:
            self.flash(u"Can not delete public version without draft.")
            return

        del public.__parent__[public.__name__]
        self.flash(u'Deleted public version.')
        self.redirect(self.url(draft, '@@edit'))


class DeleteDraft(asm.cmsui.base.ActionView):

    grok.context(asm.cms.IEdition)
    grok.name('delete-draft')

    def update(self):
        page = self.context.page
        draft = self.context.parameters.replace(
            WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
        try:
            draft = page.getEdition(draft)
        except KeyError:
            self.flash(u"No draft version to delete.")
            return

        public = self.context.parameters.replace(
            WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
        try:
            public = page.getEdition(public)
        except KeyError:
            self.flash(u"Can not delete draft without public version.")
            return

        del draft.__parent__[draft.__name__]
        self.flash(u'Deleted draft version.')
        self.redirect(self.url(public, '@@edit'))


class CreateDraft(asm.cmsui.base.ActionView):
    """Create (or update) a draft by copying the current state of the published
    edition to the draft object.

    This action view can be applied either on the draft or the public copy with
    the same result.

    """

    grok.context(asm.cms.IEdition)
    grok.name('create-draft')

    def update(self):
        page = self.context.page
        public = self.context.parameters.replace(
            WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
        try:
            public = page.getEdition(public)
        except KeyError:
            self.flash(u"Cannot revert because no public edition exists.")
            return

        draft = public.parameters.replace(WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
        draft = page.getEdition(draft, create=True)
        draft.copyFrom(public)
        self.flash(u"Copied data from public version to draft.")
        self.redirect(self.url(draft, '@@edit'))


class InconsistentStateNotification(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.base.NotificationMessages)
    grok.context(asm.cms.IEdition)

    message = u""
    instruction = u""

    def _select_public_draft_editions(self):
        edition_parameters = self.context.parameters
        page = self.context.page

        draft = None
        public = None
        if WORKFLOW_PUBLIC in edition_parameters:
            public = self.context
            parameters = edition_parameters.replace(
                WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
            try:
                draft = page.getEdition(parameters)
            except KeyError, e:
                pass
        elif WORKFLOW_DRAFT in edition_parameters:
            draft = self.context
            parameters = edition_parameters.replace(
                WORKFLOW_DRAFT, WORKFLOW_PUBLIC)
            try:
                public = page.getEdition(parameters)
            except KeyError, e:
                pass

        return public, draft


    def update(self):
        public, draft = self._select_public_draft_editions()

        if public is None or draft is None:
            return

        if self.context == draft:
            if public.modified > draft.modified:
                self.message = u"Public version has been modified after a draft has been created. Press \"Revert draft\" button to edit latest published version as a draft."
                self.instruction = u"Be careful not to lose any corrections that may have been made in the public version."
            elif draft.modified > public.modified:
                self.message = u"Remember to publish this draft."
                self.instruction = u"Changes to drafts are not visible until published."

        if self.context == public and draft.modified > public.modified:
            self.message = u"A draft exists and has been modified."
            self.instruction = u"Remember to update the draft with the same corrections you are making into the public version."
