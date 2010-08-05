# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import zope.interface


class ICMSSkin(grok.IDefaultBrowserLayer):
        grok.skin('cms')


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

