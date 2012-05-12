# Copyright (c) 2010-2011 Assembly Organizing
# See also LICENSE.txt

import BTrees.OOBTree
import asm.cms.interfaces
import datetime
import grok
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

    @property
    def tags_set(self):
        if not self.tags:
            return set()
        return set(self.tags.split(' '))

    def has_tag(self, tag):
        return tag in self.tags_set

    def list_subpages(self, type=None):
        for page in self.page.subpages:
            if type is None or page.type in type:
                yield page

grok.context(Edition)


class NullEdition(Edition):
    pass


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


@grok.subscribe(asm.cms.interfaces.IPage, grok.IObjectAddedEvent)
def add_initial_edition(page, event=None):
    page.addEdition(get_initial_parameters())


def get_initial_parameters():
    parameters = set()
    for factory in zope.component.getAllUtilitiesRegisteredFor(
            asm.cms.interfaces.IInitialEditionParameters):
        parameters.update(factory())
    return EditionParameters(parameters)



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
    annotations = zope.annotation.interfaces.IAnnotations(request)
    if 'asm.cms.edition.selectors' not in annotations:
        selectors = zope.component.subscribers(
            (request,), asm.cms.interfaces.IEditionSelector)
        annotations['asm.cms.edition.selectors'] = selectors
    for selector in annotations['asm.cms.edition.selectors']:
        preferred, acceptable = selector.select(page)
        desired = set(preferred + acceptable)
        for edition in list(scores):
            if edition not in desired:
                del scores[edition]
            if edition in set(preferred):
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


class EditionLabels(grok.GlobalUtility):

    zope.interface.implements(asm.cms.interfaces.IEditionLabels)

    def lookup(self, tag):
        prefix = tag.split(':')[0]
        labels = zope.component.getUtility(asm.cms.interfaces.IEditionLabels,
                                           name=prefix)
        return labels.lookup(tag)


class DataUri(grok.View):
    grok.context(asm.cms.interfaces.IEdition)

    def render(self):
        datauri_obj = asm.cms.interfaces.IDataUri(self.context)
        return datauri_obj.datauri
