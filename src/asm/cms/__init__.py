# Make this a Python package
import grok
import zope.app.appsetup.interfaces

def application(self):
    obj = self.context
    while obj is not None:
        if isinstance(obj, grok.Application):
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")

grok.View.application = property(fget=application)

# Provide re-exports of public API

import zope.deferredimport

zope.deferredimport.define(
    Edition='asm.cms.edition:Edition',

    Actions='asm.cms.cmsui:Actions',
    ActionView='asm.cms.cmsui:ActionView',

    Form='asm.cms.form:Form',
    EditForm='asm.cms.form:EditForm',
    AddForm='asm.cms.form:AddForm',

    # XXX Rename! This is a name clash with page.Page
    Page='asm.cms.retail:Page',

    IRetailSkin='asm.cms.interfaces:IRetailSkin',
    ICMSSkin='asm.cms.interfaces:ICMSSkin',
    IEditionFactory='asm.cms.interfaces:IEditionFactory',
    IEdition='asm.cms.interfaces:IEdition',
    IInitialEditionParameters='asm.cms.interfaces:IInitialEditionParameters',
    )
