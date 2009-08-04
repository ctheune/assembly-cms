# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import zope.interface
import zope.schema
import grok
import zc.sourcefactory.basic


class IEditionFactory(zope.interface.Interface):

    def __call__():
        """Return an edition."""


class EditionFactorySource(zc.sourcefactory.basic.BasicSourceFactory):
    """Provide the names of all edition factories as a source."""

    def getValues(self):
        return [name for name, factory in
                zope.component.getUtilitiesFor(IEditionFactory)]

    def getTitle(self, item):
        return item


class IPage(zope.interface.Interface):

    __name__ = zope.schema.TextLine(title=u'Name')
    subpages = zope.interface.Attribute('All pages below this one.')

    type = zope.schema.Choice(
        title=u'Type',
        source=EditionFactorySource())


class IEdition(zope.interface.Interface):

    parameters = zope.schema.TextLine(title=u'Edition parameters')

    def copyFrom(other):
        """Copy all content from another edition of the same kind."""


class IInitialEditionParameters(zope.interface.Interface):
    """Describes a set of parameters that should be set on initial editions
    of a page.

    """

    def __call__():
        """Return a set of parameters to be used for initial editions."""


class IHTMLPage(zope.interface.Interface):

    content = zope.schema.Text(title=u'Content')


class IAsset(zope.interface.Interface):

    content = zope.schema.Bytes(title=u'File')


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')


class IEditionSelector(zope.interface.Interface):

    def __call__(self):
        """Return a set of edition arguments to use for looking up an
        edition."""
