# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import asm.cms.utils
import grok
import megrok.pagelet
import zope.app.form.browser.source
import zope.copypastemove.interfaces
import zope.interface


class Page(grok.OrderedContainer):

    zope.interface.implements(asm.cms.interfaces.IPage)

    def __init__(self, type):
        super(Page, self).__init__()
        self.type = type

    @property
    def page(self):
        return self

    @property
    def subpages(self):
        for obj in self.values():
            if asm.cms.interfaces.IPage.providedBy(obj):
                yield obj

    @property
    def editions(self):
        for obj in self.values():
            if asm.cms.interfaces.IEdition.providedBy(obj):
                yield obj

    def getEdition(self, parameters, create=False):
        assert isinstance(parameters, asm.cms.edition.EditionParameters)
        for var in self.editions:
            if var.parameters == parameters:
                return var
        if create:
            return self.addEdition(parameters)
        raise KeyError(parameters)

    def addEdition(self, parameters):
        edition = self.factory()
        edition.parameters = asm.cms.edition.EditionParameters(parameters)
        self['edition-' + '-'.join(parameters)] = edition
        return edition

    @property
    def factory(self):
        return zope.component.getUtility(
            asm.cms.interfaces.IEditionFactory, name=self.type)

    def _add_object_to_position(self, target, obj, position=None):
        mover = zope.copypastemove.interfaces.IObjectMover(obj)
        mover.moveTo(target, obj.__name__)
        if position is None:
            return
        keys = list(target)
        keys.remove(obj.__name__)
        keys.insert(position, obj.__name__)
        target.updateOrder(keys)

    def arrange(self, obj, type):
        """Move a given object relative to this page."""

        if type not in ['inside', 'before', 'after', 'first', 'last']:
            raise ValueError("Unknown movement type %s" % type)

        if type == 'inside':
            self._add_object_to_position(self, obj)
        elif type in ['before', 'after']:
            # Insert new object before this object, or after this object.
            target = self.__parent__
            if asm.cms.get_application(self) == self:
                raise ValueError("Can not move outside this application")
            keys = list(target)
            target_position = keys.index(self.__name__)
            if type == 'after':
                target_position += 1
            self._add_object_to_position(target, obj, target_position)
        elif type == 'first':
            self._add_object_to_position(self, obj, 0)
        elif type == 'last':
            self._add_object_to_position(self, obj, len(list(self)))
