# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

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


class Navtree(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    @property
    def page(self):
        if asm.cms.interfaces.IEdition.providedBy(self.context):
            return self.context.__parent__
        return self.context

    def _create_subtree(self, root):
        tree = {'page': asm.cms.edition.select_edition(root, self.request),
                'subpages': []}
        for child in root.subpages:
            if not len(list(child.subpages)):
                continue
            tree['subpages'].append(self._create_subtree(child))
        return tree

    def tree(self):
        # Find root
        current = self.page
        while True:
            parent = current.__parent__
            if not asm.cms.interfaces.IPage.providedBy(parent):
                root = current
                break
            current = parent

        tree = [self._create_subtree(root)]
        return tree

    def css_classes(self, *classes):
        return ' '.join(filter(None, classes))


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
        self.redirect(self.url(self.context, '@@edit'))


class Actions(grok.ViewletManager):

    grok.name('actions')
    grok.context(zope.interface.Interface)


class Notes(grok.ViewletManager):

    grok.name('notes')
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
