# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import zope.interface
import zope.schema


class IPage(zope.interface.Interface):

    __name__ = zope.schema.TextLine(title=u'Name')
    content = zope.schema.Text(title=u'Content')
