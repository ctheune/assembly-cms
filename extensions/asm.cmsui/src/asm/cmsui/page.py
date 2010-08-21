# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cms.page
import asm.cmsui.base
import asm.cmsui.form
import asm.cmsui.interfaces
import grok
import zope.component
import megrok.pagelet


class Actions(grok.Viewlet):
    """Page-related UI actions to perform on editions."""

    grok.viewletmanager(asm.cmsui.base.MainPageActions)
    grok.context(asm.cms.interfaces.IEdition)

    @property
    def page(self):
        return self.context.page


class NavigationActions(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.base.NavigationActions)
    grok.context(asm.cms.interfaces.IEdition)

    def types(self):
        # XXX. Meh. Can't we re-use the widget infrastructure here?
        source = asm.cms.interfaces.EditionFactorySource()
        result = []
        for name in source.factory.getValues():
            factory = zope.component.getUtility(
                asm.cms.interfaces.IEditionFactory, name=name)
            result.append(dict(name=name,
                               factory=factory,
                               title=source.factory.getTitle(name)))
        result.sort(key=lambda x: x['factory'].factory_order)
        return result


class AddPage(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def update(self, title, type):
        page = asm.cms.page.Page(type)
        name = asm.cms.utils.normalize_name(title)
        self.context[name] = page
        edition = page.editions.next()
        edition.title = title
        self.edition = edition

    def render(self):
        return self.url(self.edition, '@@edit')


class ChangePageType(asm.cmsui.form.EditForm):

    """Changes the type of a page.

    Removes current editions but leaves sub-pages intact.

    """

    grok.context(asm.cms.interfaces.IPage)

    label = u'Change page type'
    form_fields = grok.AutoFields(asm.cms.interfaces.IPage).select('type')
    form_fields['type'].custom_widget = (
        lambda field, request: zope.app.form.browser.source.SourceRadioWidget(
                field, field.source, request))

    @grok.action('Change')
    def change(self, type):
        for edition in list(self.context.editions):
            del edition.__parent__[edition.__name__]
        self.context.type = type
        asm.cms.edition.add_initial_edition(self.context)
        self.flash(u'Page type changed to %s.' % type)
        self.redirect(self.url(
            asm.cms.edition.select_edition(self.context, self.request),
            '@@edit'))


class Delete(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def update(self):
        if isinstance(self.context, asm.cms.cms.CMS):
            self.flash('Cannot delete the root page!', 'warning')
            self.target = self.context
            return
        page = self.context
        self.target = page.__parent__
        del page.__parent__[page.__name__]
        self.flash('Page deleted.')

    def render(self):
        target = asm.cms.edition.select_edition(
            self.target, self.request)
        return self.url(target, '@@edit')


class CMSIndex(grok.View):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.context(asm.cms.interfaces.ICMS)
    grok.name('index')

    def render(self):
        try:
            edition = asm.cms.edition.select_edition(
                self.context, self.request)
        except StopIteration:
            edition = asm.cms.edition.NullEdition()
            edition.__parent__ = self.context
            edition.__name__ = ''
        self.redirect(self.url(edition, '@@edit'))


class PageIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.context(asm.cms.interfaces.IPage)
    grok.name('index')

    def render(self):
        try:
            edition = asm.cms.edition.select_edition(
                self.context, self.request)
        except StopIteration:
            edition = asm.cms.edition.NullEdition()
            edition.__parent__ = self.context
            edition.__name__ = ''
        self.redirect(self.url(edition))

# The following two views are needed to support visual editing of editions
# which have their own URL, nested a level within a page. As all relative URLs
# are constructed assuming they start from a page, we need to provide the
# means to establish a stable base URL.
#
# Note that as pages in the CMS always can act as folders we add a trailing
# slash to their URL when using them as a base: images contained in the page
# will be linked to without mentioning the name of the page explicitly.


class PageBase(grok.View):

    grok.context(asm.cms.interfaces.IPage)
    grok.name('base')

    def render(self):
        return self.url(self.context) + '/'


class EditionBase(grok.View):

    grok.name('base')
    grok.context(asm.cms.interfaces.IEdition)

    def render(self):
        return self.url(self.context.page) + '/'


class Preview(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def render(self):
        skin_name = zope.component.getUtility(asm.cms.interfaces.ISkinProfile)
        skin = zope.component.getUtility(
            zope.publisher.interfaces.browser.IBrowserSkinType, skin_name)
        edition = asm.cms.edition.select_edition(self.context, self.request)
        zope.publisher.browser.applySkin(self.request, skin)
        return zope.component.getMultiAdapter(
            (edition, self.request), zope.interface.Interface,
            name='index')()


class Arrange(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def update(self, id, type):
        iids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
        to_move = iids.getObject(int(id))
        self.context.arrange(to_move, type)

    def render(self):
        pass
