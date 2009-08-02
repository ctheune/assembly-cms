# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import zope.interface
import zope.schema
import grok


class ILocation(zope.interface.Interface):

    __name__ = zope.schema.TextLine(title=u'Name')
    sublocations = zope.interface.Attribute('All locations below this one.')


class IVariation(zope.interface.Interface):

    parameters = zope.schema.TextLine(title=u'Variation parameters')

    def copyFrom(other):
        """Copy all content from another variation of the same kind."""


class IInitialVariationCreated(zope.interface.Interface):
    """A new location was created and also an initial variation.

    The initial variation can (at this point) be annotated at this point with
    variation parameters.

    """

    variation = zope.interface.Attribute('The variation that was created')


class InitialVariationCreated(object):

    zope.interface.implements(IInitialVariationCreated)

    def __init__(self, variation):
        self.variation = variation


class IPage(zope.interface.Interface):

    content = zope.schema.Text(title=u'Content')


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')


class IVariationSelector(zope.interface.Interface):

    def __call__(self):
        """Return a set of variation arguments to use for looking up a
        variation."""
