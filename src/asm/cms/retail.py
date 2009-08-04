# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.interface


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    megrok.pagelet.template('templates/retail.pt')


class Page(megrok.pagelet.Pagelet):

    grok.baseclass()
    grok.layer(asm.cms.interfaces.IRetailSkin)
