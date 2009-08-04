import grok
import asm.cms
import megrok.pagelet
import zope.interface

class ISummer09(asm.cms.IRetailSkin):
    grok.skin('summer09')

class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISummer09)
    megrok.pagelet.template('layout.pt')
