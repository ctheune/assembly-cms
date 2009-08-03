# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet
import zope.interface
import asm.cms.location
import asm.cms.interfaces


class CMS(grok.Application, asm.cms.location.Location):
    type = 'page'


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    megrok.pagelet.template('templates/layout.pt')


class Navtree(grok.View):
    grok.context(zope.interface.Interface)
