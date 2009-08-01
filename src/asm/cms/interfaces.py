# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import zope.interface
import zope.schema
import grok


class IPage(zope.interface.Interface):

    __name__ = zope.schema.TextLine(title=u'Name')
    content = zope.schema.Text(title=u'Content')


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')
