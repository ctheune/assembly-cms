# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import z3c.flashmessage.interfaces
import cgi
import asm.cms.edition
import asm.cms.interfaces
import datetime
import grok
import megrok.pagelet
import zope.interface


class EditContent(grok.Permission):
    grok.name('asm.cms.EditContent')


class Layout(megrok.pagelet.Layout):

    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    megrok.pagelet.template('templates/cms.pt')

    def __call__(self):
        raise zope.security.interfaces.Unauthorized()


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)

    def render(self):
        return ''

    def breadcrumbs(self):
        pages = []
        page = self.context.page
        while not isinstance(page, asm.cms.cms.CMS):
            pages.insert(0, asm.cms.edition.select_edition(page, self.request))
            page = page.__parent__
        return pages

    def messages(self):
        receiver = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageReceiver)
        return receiver.receive()


class Tree(grok.View):

    grok.context(grok.Application)   # XXX Meh.
    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.request.response.setHeader('Content-Type', 'text/xml')

    def _sub_projects(self, root):
        intids = zope.component.getUtility(zope.app.intid.IIntIds)
        edition = asm.cms.edition.select_edition(root, self.request)
        if isinstance(edition, asm.cms.edition.NullEdition):
            # XXX
            return ''
        html = '<item rel="%s" id="%s">\n' % (root.type,
                                               intids.getId(edition))
        html += '<content><name href="%s">%s</name></content>\n' % (
            self.url(edition, '@@edit'), cgi.escape(edition.title))
        for sub in root.subpages:
            html += self._sub_projects(sub)
        html += "</item>\n"
        return html

    def tree(self):
        html = "<root>\n%s" % self._sub_projects(self.context)
        html += "</root>\n"
        return html


class PageHeader(grok.ViewletManager):
    grok.context(zope.interface.Interface)
    grok.name('pageheader')


class Breadcrumbs(grok.Viewlet):
    grok.viewletmanager(PageHeader)
    grok.context(asm.cms.interfaces.IEdition)


class NavDetails(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def pages(self):
        if not asm.cms.interfaces.IPage.providedBy(self.context):
            page = self.context.page
        else:
            page = self.context
        for subpage in page.subpages:
            yield asm.cms.edition.select_edition(subpage, self.request)


class ActionView(grok.View):

    grok.baseclass()
    grok.layer(asm.cms.interfaces.ICMSSkin)

    def render(self):
        self.redirect(self.url(self.context))


class MainPageActions(grok.ViewletManager):

    grok.name('main-page-actions')
    grok.context(zope.interface.Interface)


class ExtendedPageActions(grok.ViewletManager):

    grok.name('extended-page-actions')
    grok.context(zope.interface.Interface)


class PageActionGroups(grok.ViewletManager):

    grok.name('page-action-groups')
    grok.context(zope.interface.Interface)


class NavigationActions(grok.ViewletManager):

    grok.name('navigation-actions')
    grok.context(zope.interface.Interface)


class DateFormat(grok.View):

    grok.context(datetime.datetime)
    grok.name('format')

    def render(self):
        # XXX L10N or simple 'XXX time ago'
        return self.context.strftime('%d.%m.%Y %H:%M')


class BytesFormat(grok.View):

    grok.context(int)

    units = ['Bytes', 'KiB', 'MiB', 'GiB']

    def render(self):
        size = float(self.context)
        units = self.units[:]
        unit = units.pop(0)

        while size >= (1024 / 2) and units:
            size = size / 1024
            unit = units.pop(0)

        size = '%.1f' % size
        size = size.replace('.0', '')

        return '%s %s' % (size, unit)


class NoneFormat(grok.View):
    grok.name('format')
    grok.context(None.__class__)

    def render(self):
        return ''
