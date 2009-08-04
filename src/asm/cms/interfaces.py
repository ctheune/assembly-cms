# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import zope.interface
import zope.schema
import grok
import zc.sourcefactory.basic


class IVariationFactory(zope.interface.Interface):

    def __call__():
        """Return a variation."""


class VariationFactorySource(zc.sourcefactory.basic.BasicSourceFactory):
    """Provide the names of all variation factories as a source."""

    def getValues(self):
        return [name for name, factory in
                zope.component.getUtilitiesFor(IVariationFactory)]

    def getTitle(self, item):
        return item


class ILocation(zope.interface.Interface):

    __name__ = zope.schema.TextLine(title=u'Name')
    sublocations = zope.interface.Attribute('All locations below this one.')

    type = zope.schema.Choice(
        title=u'Type',
        source=VariationFactorySource())


class IVariation(zope.interface.Interface):

    parameters = zope.schema.TextLine(title=u'Variation parameters')

    def copyFrom(other):
        """Copy all content from another variation of the same kind."""


class IInitialVariationParameters(zope.interface.Interface):
    """Describes a set of parameters that should be set on initial variations
    of a location.

    """

    def __call__():
        """Return a set of parameters to be used for initial variations."""


class IPage(zope.interface.Interface):

    content = zope.schema.Text(title=u'Content')


class IAsset(zope.interface.Interface):

    content = zope.schema.Bytes(title=u'File')


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')


class IVariationSelector(zope.interface.Interface):

    def __call__(self):
        """Return a set of variation arguments to use for looking up a
        variation."""
