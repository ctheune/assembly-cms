# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.utils
import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.app.form.browser.source
import zope.interface
import zope.copypastemove.interfaces


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
