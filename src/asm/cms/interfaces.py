# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import zope.interface
import zope.schema


class IPage(zope.interface.Interface):

    body = zope.schema.Text(title=u'Content')
