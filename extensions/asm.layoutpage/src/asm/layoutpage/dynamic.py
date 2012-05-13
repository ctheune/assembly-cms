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

def _create_navigation_subtree(active, root_page, levels, request):
    if levels < 0:
        return
    if root_page.type in ['asset']:
        return
    edition = asm.cms.edition.select_edition(root_page, request)
    if edition.has_tag('hide-navigation'):
        return
    if isinstance(edition, asm.cms.edition.NullEdition):
        return
    tree = {'page': edition,
            'class': set(),
            'subpages': []}
    if root_page in active:
        tree['class'].add('active')
        if root_page.type not in ['news']:
            for child in root_page.subpages:
                sub_tree = _create_navigation_subtree(active, child, levels - 1, request)
                if sub_tree:
                    tree['subpages'].append(sub_tree)
    if 'active' in tree['class'] and not tree['subpages']:
        tree['class'].add('has_no_children')
    tree['class'] = ' '.join(tree['class'])
    return tree


class SectionNavigation(grok.View):
    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def find_section(self, root=None):
        if root is None:
            root = self.application
        candidate = self.context
        while candidate != root:
            if candidate.__parent__ == root:
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

    def tree(self):
        root = self.find_section()
        tree = _create_navigation_subtree(self.active, root, NAVTREE_MAX_LEVELS, self.request)
        return tree['subpages']


class SubSectionNavigation(SectionNavigation):
    grok.template("sectionnavigation")

    def find_subsection(self):
        section = self.find_section()
        if section is None:
            return
        return self.find_section(root=section)

    def tree(self):
        root_edition = self.find_subsection()
        root = root_edition.page
        tree = _create_navigation_subtree(self.active, root, NAVTREE_MAX_LEVELS, self.request)
        return tree['subpages']


class BaseUrl(grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def render(self):
        return self.application_url()



