# Copyright (c) 2011 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import zope.interface

class Redirect(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IRedirect)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Redirect'

    target_url = None

    def copyFrom(self, other):
        super(Redirect, self).copyFrom(other)
        self.target_url = other.target_url

    def __eq__(self, other):
        if not super(Redirect, self).__eq__(other):
            return False
        return self.target_url == other.target_url
