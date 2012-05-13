import grok
import asm.cms.interfaces
import asm.cmsui.interfaces
import asm.cms.edition


class TileNavigation(grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def update(self):
        self.rows = []
        row = []
        for edition in asm.cms.edition.find_editions(self.context.page, self.request,
                recurse=False):
            if edition.has_tag('hide-navigation'):
                continue
            if len(row) == 3:
                self.rows.append(row)
                row = []
            row.append(edition)

        self.rows.append(row)

NAVTREE_MAX_LEVELS = 999

class SectionNavigation(grok.View):
    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def find_section(self):
        candidate = self.context
        while candidate != self.application:
            if candidate.__parent__ == self.application:
                return candidate
            candidate = candidate.__parent__

    def update(self):
        self.section = self.find_section()
        self.subsections = []
        for edition in asm.cms.edition.find_editions(self.section, self.request,
                recurse=False):
            if edition.has_tag('hide-navigation'):
                continue
            self.subsections.append(edition)

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
            if root.type not in ['news']:
                for child in root.subpages:
                    sub_tree = self._create_subtree(child, levels - 1)
                    if sub_tree:
                        tree['subpages'].append(sub_tree)
        if 'active' in tree['class'] and not tree['subpages']:
            tree['class'].add('has_no_children')
        tree['class'] = ' '.join(tree['class'])
        return tree

    def tree(self):
        root = self.find_section()
        tree = self._create_subtree(root, NAVTREE_MAX_LEVELS)
        return tree['subpages']


class BaseUrl(grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def render(self):
        return self.application_url()



