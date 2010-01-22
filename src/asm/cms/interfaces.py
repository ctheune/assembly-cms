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


class IExtensionPrefixes(zope.interface.Interface):

    prefixes = zope.interface.Attribute(
        'A set of prefixes defined by an extension')


class IPage(zope.interface.Interface):

    __name__ = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the page will be used in the URL.')
    subpages = zope.interface.Attribute('All pages below this one.')

    type = zope.schema.Choice(
        title=u'Type',
        source=EditionFactorySource())


class ICMS(IPage):
    """A page that is the root CMS object."""


class IEdition(zope.interface.Interface):

    parameters = zope.schema.TextLine(title=u'Edition parameters')
    title = zope.schema.TextLine(title=u'Title')
    tags = zope.schema.TextLine(title=u'Tags', required=False)

    created = zope.schema.Datetime(title=u'Created', readonly=True)
    modified = zope.schema.Datetime(title=u'Last change', readonly=True)

    size = zope.schema.Int(title=u'Size', readonly=True)

    def copyFrom(other):
        """Copy all content from another edition of the same kind."""


class IInitialEditionParameters(zope.interface.Interface):
    """Describes a set of parameters that should be set on initial editions
    of a page.

    """

    def __call__():
        """Return a set of parameters to be used for initial editions."""


class IHTMLPage(zope.interface.Interface):

    content = zope.schema.Text(title=u'Page content')


class IAsset(zope.interface.Interface):

    content = zope.schema.Bytes(title=u'File', required=False)
    content_type = zope.schema.ASCIILine(title=u'Content Type', readonly=True)


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')


class IEditionSelector(zope.interface.Interface):

    preferred = zope.interface.Attribute('A list of preferred editions.')
    acceptable = zope.interface.Attribute('A list of acceptable editions')


class ISearchableText(zope.interface.Interface):

    body = zope.interface.Attribute(
        "A unicode string containing text for indexing.")


class IReplaceSupport(zope.interface.Interface):

    def search(term):
        """Searches for the given term and returns IReplaceOccurence
        objects."""
        pass


class IReplaceOccurence(zope.interface.Interface):

    preview = zope.interface.Attribute(
        'Return preview text that shows the occurence in context and'
        'highlights it with a span tag.')

    id = zope.interface.Attribute(
        'Return a string ID that can be used to identify this'
        'occurence again later')

    def replace(target):
        """Replace this occurence in the original text with the target."""


class IAdditionalSchema(zope.interface.Interface):
    """Provides an additional schema to transparently extend
    edition objects."""
