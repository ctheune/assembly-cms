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
        for section in asm.cms.edition.find_editions(root, request=self.request,
                                                 recurse=False):
            if section.tags and 'navigation' in section.tags:
                yield section

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


class Homepage(asm.cmsui.retail.Pagelet):
    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('index')

    def news(self, tag):
        if 'news' not in self.context.page:
           raise StopIteration() 
        
        news_edition = asm.cms.edition.select_edition(
            self.context.page['news'], self.request)
        for item in news_edition.list():
            edition = asm.cms.edition.select_edition(
                item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            if not edition.has_tag(tag):
                continue
            result = dict(edition=edition,
                          news=asm.cms.news.INewsFields(edition))
            if result['news'].image:
                result['teaser_url'] = self.url(edition.page['teaser-image'])
            else:
                result['teaser_url'] = ''
            yield result

    def featured(self):
        return sorted(self.news('featured'),
                      key=lambda x: x['edition'].modified,
                      reverse=True)

    def frontpage(self):
        return list(sorted(self.news('frontpage'),
                           key=lambda x: x['edition'].modified,
                           reverse=True))[:12]


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))
