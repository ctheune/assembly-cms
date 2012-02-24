# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import ZODB.blob
import zc.sourcefactory.basic
import zope.component
import zope.interface
import zope.schema


class IEditionFactory(zope.interface.Interface):

    def __call__():
        """Return an edition."""


class EditionFactorySource(zc.sourcefactory.basic.BasicSourceFactory):
    """Provide the names of all edition factories as a source."""

    def getValues(self):
        return [name for name, factory in
                zope.component.getUtilitiesFor(IEditionFactory)]

    def getTitle(self, item):
        factory = zope.component.getUtility(IEditionFactory, name=item)
        return getattr(factory, 'factory_title', item)


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

    def copyFrom(other):
        """Copy all content from another edition of the same kind."""

    def __eq__(other):
        """Check whether the content of the other edition is the same as this.

        Does not include creation and modification dates and the edition
        parameters.

        """


class IInitialEditionParameters(zope.interface.Interface):
    """Describes a set of parameters that should be set on initial editions
    of a page.

    """

    def __call__():
        """Return a set of parameters to be used for initial editions."""


class IHTMLPage(zope.interface.Interface):

    content = zope.schema.Text(title=u'Page content')


class Blob(zope.schema.Field):

    _type = ZODB.blob.Blob


class IAsset(zope.interface.Interface):

    content = Blob(title=u'File', required=False)
    content_type = zope.schema.ASCIILine(title=u'Content Type', readonly=True)
    size = zope.schema.Int(title=u'Size of this asset', readonly=True)


class IEditionSelector(zope.interface.Interface):

    def select(page):
        """Returns a tuple with sets of editions (preferred, acceptable)."""


class IEditionLabels(zope.interface.Interface):

    def lookup(tag):
        """Return a label for a tag."""


class ISearchableText(zope.interface.Interface):

    body = zope.interface.Attribute(
        "A Unicode string containing text for indexing.")


class IIndexedContent(ISearchableText):
    """A wrapper interface to accumulate the various indexes for
    flexibility."""


class IReplaceSupport(zope.interface.Interface):

    def search(term):
        """Searches for the given term and returns IReplaceOccurrence
        objects."""
        pass


class IReplaceOccurrence(zope.interface.Interface):

    preview = zope.interface.Attribute(
        'Return preview text that shows the occurrence in context and'
        'highlights it with a span tag.')

    id = zope.interface.Attribute(
        'Return a string ID that can be used to identify this'
        'occurrence again later')

    def replace(target):
        """Replace this occurrence in the original text with the target."""


class IAdditionalSchema(zope.interface.Interface):
    """Provides an additional schema to transparently extend
    edition objects."""

    def copyFrom(other):
        """Copy all content from another edition of the same kind."""

    def __eq__(other):
        """Check whether the content of the other edition is the same as this.

        """


class IProfile(zope.component.interfaces.IComponents):
    """A component registry defining an Assembly CMS profile."""


class ISkinProfile(zope.interface.Interface):
    """The name of the skin in a profile."""


class ProfileSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return [name for name, profile in
                zope.component.getUtilitiesFor(IProfile)]


class IProfileSelection(zope.interface.Interface):

    name = zope.schema.Choice(
        title=u'Profile',
        source=ProfileSource())

class ISearchSites(zope.interface.Interface):

    sites = zope.schema.List(
        title=u'Sites',
        value_type=zope.schema.URI(title=u'Query URL'))


class IImport(zope.interface.Interface):

    data = zope.schema.Bytes(
        title=u'Content',
        description=(u'The content is expected to be in the Assembly CMS '
                     u'XML import format.'))


class IContentImported(zope.interface.Interface):
    """Content was imported into a CMS site."""

    site = zope.interface.Attribute("The site that content was imported to.")
    errors = zope.interface.Attribute(
        "A list with textual descriptions of errors.")


class IRedirect(zope.interface.Interface):
    target_url = zope.schema.URI(title=u'Redirect URI')


class IDataUri(zope.interface.Interface):
    datauri = zope.schema.URI(title=u'Data URI')

