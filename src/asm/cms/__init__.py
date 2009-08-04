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
    Variation='asm.cms.location:Variation',
    Actions='asm.cms.location:Actions',

    Form='asm.cms.form:Form',
    EditForm='asm.cms.form:EditForm',
    AddForm='asm.cms.form:AddForm',

    Page='asm.cms.retail:Page',

    IRetailSkin='asm.cms.interfaces:IRetailSkin',
    ICMSSkin='asm.cms.interfaces:ICMSSkin',
    IVariationFactory='asm.cms.interfaces:IVariationFactory',
    IVariation='asm.cms.interfaces:IVariation',
    IInitialVariationParameters='asm.cms.interfaces:IInitialVariationParameters',

    ActionView='asm.cms.cms:ActionView')
