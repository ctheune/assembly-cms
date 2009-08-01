# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet
import zope.interface
import asm.cms.page


class CMS(grok.Application, asm.cms.page.Page):
    pass


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)

    megrok.pagelet.template('templates/cms-owrap.pt')
