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

from asm.cms.location import Variation
from asm.cms.form import Form, EditForm, AddForm
from asm.cms.interfaces import IRetailSkin, ICMSSkin, IVariationFactory
