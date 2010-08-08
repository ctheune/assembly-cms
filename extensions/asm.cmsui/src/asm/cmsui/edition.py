# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt


class ExtendedPageActions(grok.Viewlet):

    grok.viewletmanager(asm.cms.ExtendedPageActions)
    grok.context(Edition)


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


class NullIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.name('index')
    grok.context(NullEdition)

    def render(self):
        return 'No edition available.'
