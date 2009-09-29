# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
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
            if child.type == 'asset':
                continue
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
        sort_tree(tree)
        return tree


class NavDetails(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')


def sort_tree(tree):
    tree.sort(key=lambda x:x['page'].page.__name__)
    for x in tree:
        sort_tree(x['subpages'])


class ActionView(grok.View):

    grok.baseclass()
    grok.layer(asm.cms.interfaces.ICMSSkin)

    def render(self):
        self.redirect(self.url(self.context))


class Actions(grok.ViewletManager):
    grok.name('actions')
    grok.context(zope.interface.Interface)


@grok.adapter(asm.cms.interfaces.IEdition, asm.cms.interfaces.IRetailSkin)
@grok.implementer(zope.traversing.browser.interfaces.IAbsoluteURL)
def edition_url(edition, request):
    return zope.component.getMultiAdapter(
        (edition.__parent__, request),
        zope.traversing.browser.interfaces.IAbsoluteURL)
