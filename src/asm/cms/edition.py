# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import BTrees.OOBTree
import asm.cms.interfaces
import datetime
import grok
import megrok.pagelet
import pytz
import re
import zope.interface


class Edition(grok.Model):

    zope.interface.implements(asm.cms.interfaces.IEdition)

    created = None
    modified = None
    tags = None
    title = u''

    def __init__(self):
        super(Edition, self).__init__()
        self.parameters = BTrees.OOBTree.OOTreeSet()
        self.date_created = datetime.datetime.now()
        self.date_modified = self.date_created

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
        zope.event.notify(grok.ObjectModifiedEvent(self))


grok.context(Edition)


class NullEdition(Edition):
    pass


class NullIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.ICMSSkin)
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


@grok.subscribe(asm.cms.interfaces.IPage, grok.IObjectAddedEvent)
def add_initial_edition(page, event):
    parameters = set()
    for factory in zope.component.getAllUtilitiesRegisteredFor(
            asm.cms.interfaces.IInitialEditionParameters):
        parameters.update(factory())
    page.addEdition(parameters)


class Delete(grok.View):

    grok.context(Edition)

    def update(self):
        page = self.context.__parent__
        self.target = page
        del page[self.context.__name__]

    def render(self):
        self.redirect(self.url(self.target))


class Actions(grok.Viewlet):

    grok.viewletmanager(asm.cms.Actions)
    grok.context(Edition)


# XXX The following viewlet setup is a bit annoying: we register a viewlet for
# displaying all editions when looking at a page and when looking at a
# specific edition. The code is basically the same each time (we actually
# re-use the template), but the amount of registration necessary is just bad.

class Editions(grok.ViewletManager):
    grok.name('editions')
    grok.context(zope.interface.Interface)


class PageEditions(grok.Viewlet):
    grok.viewletmanager(Editions)
    grok.context(zope.interface.Interface)
    grok.template('editions')


class TinyMCELinkBrowsers(grok.View):

    grok.name('tinymce-linkbrowser')
    grok.template('tinymce-linkbrowser')


@grok.subscribe(asm.cms.interfaces.IEdition, grok.IObjectModifiedEvent)
def annotate_modification_date(obj, event):
    obj.modified = datetime.datetime.now(pytz.UTC)


@grok.subscribe(Edition, grok.ObjectAddedEvent)
def annotate_creation_date(obj, event):
    obj.created = datetime.datetime.now(pytz.UTC)
