# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import megrok.pagelet
import grok
import asm.cmsui.interfaces
import asm.cms.edition
import asm.cmsui.cmsui
import zope.interface


class NullIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.name('index')
    grok.context(asm.cms.edition.NullEdition)

    def render(self):
        return 'No edition available.'


class DisplayParameters(grok.View):
    grok.context(asm.cms.edition.EditionParameters)
    grok.name('index')

    def render(self):
        # XXX use better lookup mechanism for tag labels
        tags = sorted(self.context)
        labels = zope.component.getUtility(asm.cms.interfaces.IEditionLabels)
        return '(%s)' % ', '.join(labels.lookup(tag) for tag in tags)


class ExtendedPageActions(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.cmsui.ExtendedPageActions)
    grok.context(asm.cms.edition.Edition)


# Issue #59: The following viewlet setup is a bit annoying: we register a
# viewlet for displaying all editions when looking at a page and when looking
# at a specific edition. The code is basically the same each time (we actually
# re-use the template), but the amount of registration necessary is just bad.


class Editions(grok.ViewletManager):

    grok.name('editions')
    grok.context(zope.interface.Interface)


class PageEditions(grok.Viewlet):
    grok.viewletmanager(Editions)
    grok.context(zope.interface.Interface)
    grok.template('editions')

class ImagePicker(grok.View):
    grok.context(Edition)
    grok.name('image-picker')


