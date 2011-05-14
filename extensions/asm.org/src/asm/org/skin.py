import asm.cms
import asm.cmsui.retail
import asm.cmsui.interfaces
import datetime
import grok
import megrok.pagelet
import zope.interface

asmorg = asm.cms.cms.Profile('asmorg')
languages = ['en', 'fi']
skin_name = 'asmorg'


class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin(skin_name)


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    def sections(self):
        root = self.application
        for section in asm.cms.edition.find_editions(
                root, request=self.request, recurse=False):
            if section.tags and 'navigation' in section.tags:
                yield section

    def sub_sections(self):
        candidate = self.context.page
        while candidate is not None:
            if asm.cms.interfaces.ICMS.providedBy(candidate.__parent__):
                break
            candidate = candidate.__parent__
        else:
            return
        return dict(section=asm.cms.edition.select_edition(
                        candidate, self.request),
                    subs=asm.cms.edition.find_editions(
                        candidate, request=self.request, recurse=False))

    # A helper class to get access to the static directory in this module from
    # the layout.

    def render(self):
        return ''


class Navtree(grok.View):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)

    def update(self):
        self.active = []
        current = self.context.page
        while current:
            self.active.append(current)
            current = current.__parent__

    def _create_subtree(self, root, levels):
        if levels < 0:
            return
        if root.type in ['asset']:
            return
        edition = asm.cms.edition.select_edition(root, self.request)
        if edition.has_tag('hide-navigation'):
            return
        if isinstance(edition, asm.cms.edition.NullEdition):
            return
        tree = {'page': edition,
                'class': set(),
                'subpages': []}
        if root in self.active:
            tree['class'].add('active')
            for child in root.subpages:
                sub_tree = self._create_subtree(child, levels - 1)
                if sub_tree:
                    tree['subpages'].append(sub_tree)
        if 'active' in tree['class'] and not tree['subpages']:
            tree['class'].add('has_no_children')
        tree['class'] = ' '.join(tree['class'])
        return tree

    def tree(self):
        root = self.application

        tree = self._create_subtree(root, 3)
        return tree['subpages']

    @property
    def page(self):
        if asm.cms.interfaces.IEdition.providedBy(self.context):
            return self.context.__parent__
        return self.context

    def css_classes(self, *classes):
        return ' '.join(filter(None, classes))
