# Copyright (c) 2011 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import grok
import zope.interface
import zope.publisher.interfaces.browser
import zope.traversing.browser.interfaces

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

class RedirectAbsoluteUrl(grok.MultiAdapter):
    grok.adapts(
        asm.cms.interfaces.IRedirect,
        zope.publisher.interfaces.browser.IBrowserRequest)
    grok.implements(zope.traversing.browser.interfaces.IAbsoluteURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.context.target_url
