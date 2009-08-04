# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import grok
import megrok.pagelet
import zope.interface


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    megrok.pagelet.template('templates/layout.pt')


class Navtree(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cms.interfaces.ICMSSkin)

    @property
    def page(self):
        if asm.cms.interfaces.IEdition.providedBy(self.context):
            return self.context.__parent__
        return self.context

    def tree(self):
        tree = None

        # Add parents
        current = self.page
        while asm.cms.interfaces.IPage.providedBy(current):
            new_tree = {'page': current, 'subpages': []}
            if tree is not None:
                new_tree['subpages'].append(tree)
            tree = new_tree
            # Add direct children
            for child in current.subpages:
                if child in [x['page'] for x in tree['subpages']]:
                    continue
                tree['subpages'].append({'page': child, 'subpages': []})
            current = current.__parent__

        tree = [tree]
        sort_tree(tree)
        return tree


def sort_tree(tree):
    tree.sort(key=lambda x:x['page'].__name__)
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
