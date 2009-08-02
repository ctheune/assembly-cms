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


class IPage(zope.interface.Interface):

    content = zope.schema.Text(title=u'Content')


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')
