# Copyright (c) 2010 Assembly Organizing
# See also LICENSE.txt

import BTrees.OOBTree
import asm.cms.interfaces
import datetime
import grok
import megrok.pagelet
import pytz
import re
import sys
import zope.interface


class Edition(grok.Model):

    grok.implements(asm.cms.interfaces.IEdition)

    factory_visible = False
    factory_order = sys.maxint

    created = None
    modified = None
    tags = None
    title = u''

    size = 0

    def __init__(self):
        super(Edition, self).__init__()
        self.parameters = BTrees.OOBTree.OOTreeSet()

    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        for schema in zope.component.subscribers(
                (self,), asm.cms.interfaces.IAdditionalSchema):
            if not schema(self) == schema(other):
                return False
        return (self.tags == other.tags and
                self.title == other.title)

    @property
    def editions(self):
        return self.__parent__.editions

    @property
    def page(self):
        return self.__parent__

    def copyFrom(self, other):
        self.created = other.created
        self.modified = other.modified
        self.tags = other.tags
        self.title = other.title
        for schema in zope.component.subscribers(
                (self,), asm.cms.interfaces.IAdditionalSchema):
            schema(self).copyFrom(schema(other))

        zope.event.notify(grok.ObjectModifiedEvent(self))
        # Workaround: if we copyFrom we also want to take over the
        # modification date as we didn't change anything, yet.
        self.modified = other.modified

    def has_tag(self, tag):
        if not self.tags:
            return False
        tags = self.tags.split(' ')
        return tag in tags


grok.context(Edition)


class NullEdition(Edition):
    pass


class NullIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.name('index')
    grok.context(NullEdition)

    def render(self):
        return 'No edition available.'


class EditionParameters(object):
    """Edition parameters are used to differentiate editions from each other.

    Parameters are immutable. All mutating operations on parameters thus
    return a mutated copy of the parameters.

    """

    def __init__(self, initial=()):
        self.parameters = set(initial)

    def __eq__(self, other):
        if not other:
            return False
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

    def by_prefix(self, prefix):
        prefix = prefix + ':'
        for parameter in self:
            if parameter.startswith(prefix):
                yield parameter[len(prefix):]


class DisplayParameters(grok.View):
    grok.context(EditionParameters)
    grok.name('index')

    def render(self):
        # XXX use better lookup mechanism for tag labels
        tags = sorted(self.context)
        labels = zope.component.getUtility(asm.cms.interfaces.IEditionLabels)
        return '(%s)' % ', '.join(labels.lookup(tag) for tag in tags)


@grok.subscribe(asm.cms.interfaces.IPage, grok.IObjectAddedEvent)
def add_initial_edition(page, event=None):
    page.addEdition(get_initial_parameters())


def get_initial_parameters():
    parameters = set()
    for factory in zope.component.getAllUtilitiesRegisteredFor(
            asm.cms.interfaces.IInitialEditionParameters):
        parameters.update(factory())
    return EditionParameters(parameters)


class Delete(grok.View):
    """Deletes an edition."""

    grok.context(Edition)

    def update(self):
        page = self.context.__parent__
        self.target = asm.cms.edition.select_edition(
            page, self.request)
        del page[self.context.__name__]

    def render(self):
        self.redirect(self.url(self.target, '@@edit'))


class ExtendedPageActions(grok.Viewlet):

    grok.viewletmanager(asm.cms.ExtendedPageActions)
    grok.context(Edition)


# Issue #59: The following viewlet setup is a bit annoying: we register a
# viewlet for displaying all editions when looking at a page and when looking
# at a specific edition. The code is basically the same each time (we actually
# re-use the template), but the amount of registration necessary is just bad.


class Editions(grok.ViewletManager):

    grok.name('editions')
    grok.context(zope.interface.Interface)


class PageEditions(grok.Viewlet):
    grok.viewletmanager(Editions)
    grok.context(zope.interface.Interface)
    grok.template('editions')


@grok.subscribe(asm.cms.interfaces.IEdition, grok.IObjectModifiedEvent)
def annotate_modification_date(obj, event):
    obj.modified = datetime.datetime.now(pytz.UTC)


@grok.subscribe(Edition, grok.ObjectAddedEvent)
def annotate_creation_date(obj, event):
    obj.created = obj.modified = datetime.datetime.now(pytz.UTC)


def select_edition(page, request):
    """Select the most appropriate edition of the page in the context of the
    given request.

    This function consults IEditionSelector objects to categorize all editions
    of the page into one of three categories:

    - undesired
    - acceptable
    - preferred

    Whenever at least one edition selector finds an edition undesired it can
    never be the result of selection_edition.

    """
    # Track the score for all editions, starting with 0.
    scores = dict((x, 0) for x in page.editions)

    # Consult all edition selectors
    selectors = zope.component.subscribers(
        (page, request), asm.cms.interfaces.IEditionSelector)
    for selector in selectors:
        desired = set(selector.preferred + selector.acceptable)
        for edition in list(scores):
            if edition not in desired:
                del scores[edition]
            if edition in set(selector.preferred):
                # XXX the above condition needs a test: we used to apply the
                # __contains__ test on the list but that causes problems
                # because lists use __eq__ where as we need __hash__ for
                # comparison.
                scores[edition] += 1

    # In case that the selectors found all the existing editions undesirable,
    # we bail out with a dummy.
    if not scores:
        null = NullEdition()
        null.__parent__ = page
        null.__name__ = u''
        return null

    # Select one of the editions that has the highest score.
    scores = scores.items()
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0]


def find_editions(root, request=None, schema=zope.interface.Interface, recurse=True):
    for page in root.subpages:
        if request is not None:
            editions = [select_edition(page, request)]
        else:
            editions = page.editions
        for edition in editions:
            try:
                edition = schema(edition)
            except TypeError:
                continue
            yield edition
    if recurse:
        for page in root.subpages:
            for sub in find_editions(page, request, schema):
                yield sub


class ImagePicker(grok.View):
    grok.context(Edition)
    grok.name('image-picker')


class EditionLabels(grok.GlobalUtility):

    zope.interface.implements(asm.cms.interfaces.IEditionLabels)

    def lookup(self, tag):
        prefix = tag.split(':')[0]
        labels = zope.component.getUtility(asm.cms.interfaces.IEditionLabels,
                                           name=prefix)
        return labels.lookup(tag)
