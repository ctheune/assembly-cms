# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.cmsui
import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.app.form.browser.source
import zope.interface


class Page(grok.OrderedContainer):

    zope.interface.implements(asm.cms.interfaces.IPage)

    @property
    def subpages(self):
        for obj in self.values():
            if asm.cms.interfaces.IPage.providedBy(obj):
                yield obj

    @property
    def editions(self):
        for obj in self.values():
            if asm.cms.interfaces.IEdition.providedBy(obj):
                yield obj

    def getEdition(self, parameters, create=False):
        assert isinstance(parameters, asm.cms.edition.EditionParameters)
        for var in self.editions:
            if var.parameters == parameters:
                return var
        if create:
            return self.addEdition(parameters)
        raise KeyError(parameters)

    def addEdition(self, parameters):
        edition = self.factory()
        edition.parameters = asm.cms.edition.EditionParameters(parameters)
        self['edition-' + '-'.join(parameters)] = edition
        return edition

    @property
    def factory(self):
        return zope.component.getUtility(
            asm.cms.interfaces.IEditionFactory, name=self.type)


class AddPage(asm.cms.form.AddForm):

    grok.context(asm.cms.interfaces.IPage)

    label = u'Add page'
    form_fields = grok.AutoFields(asm.cms.interfaces.IPage)
    form_fields['type'].custom_widget = (
        lambda field, request: zope.app.form.browser.source.SourceRadioWidget(
                field, field.source, request))

    factory = Page

    def chooseName(self, obj):
        return obj.__name__

    def add(self, obj):
        name = self.chooseName(obj)
        self.context[name] = obj
        self.target = asm.cms.edition.select_edition(obj, self.request)


class ChangePageType(asm.cms.form.EditForm):
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
        for edition in self.context.editions:
            del edition.__parent__[edition.__name__]
        self.context.type = type
        asm.cms.edition.add_initial_edition(self.context)
        self.flash(u'Page type changed to %s.' % type)
        self.redirect(self.url(list(self.context.editions)[0], '@@edit'))


class Delete(grok.View):

    grok.context(asm.cms.interfaces.IPage)

    def update(self):
        if isinstance(self.context, asm.cms.cms.CMS):
            raise TypeError("Can not delete CMS instances.")
        page = self.context
        self.target = page.__parent__
        del page.__parent__[page.__name__]

    def render(self):
        self.redirect(self.url(self.target))


class PageActions(grok.Viewlet):

    grok.viewletmanager(asm.cms.cmsui.Actions)
    grok.context(asm.cms.interfaces.IEdition)
    grok.template('actions')

    @property
    def page(self):
        return self.context.page


class Actions(grok.Viewlet):
    # XXX We need to repeat ourselves here: page actions are actions for pages
    # shown on editions. Actions are those shown on pages themselves
    grok.viewletmanager(asm.cms.cmsui.Actions)
    grok.context(asm.cms.interfaces.IPage)

    @property
    def page(self):
        return self.context


class RetailIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.IRetailSkin)
    grok.context(asm.cms.interfaces.IPage)
    grok.name('edit')
    grok.template('index')


class CMSEdit(megrok.pagelet.Pagelet):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.context(asm.cms.interfaces.IPage)
    grok.require('asm.cms.EditContent')
    grok.name('edit')
    grok.template('index')


class CMSIndex(grok.View):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.context(asm.cms.interfaces.IPage)
    grok.name('index')

    def render(self):
        try:
            edition = self.context.editions.next()
        except StopIteration:
            edition = asm.cms.edition.NullEdition()
            edition.__parent__ = self.context
            edition.__name__ = ''
        return zope.component.getMultiAdapter(
            (edition, self.request), name='index')()


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
        skin = zope.component.getUtility(
            zope.publisher.interfaces.browser.IBrowserSkinType, 'summer09')
        edition = asm.cms.edition.select_edition(self.context, self.request)
        zope.publisher.browser.applySkin(self.request, skin)
        return zope.component.getMultiAdapter(
            (edition, self.request), zope.interface.Interface,
            name='index')()
