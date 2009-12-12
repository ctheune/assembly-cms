import asm.cms
import asm.cms.cmsui
import datetime
import grok
import megrok.pagelet
import time
import zope.interface
import pytz


class ISummer09(asm.cms.IRetailSkin):
    grok.skin('summer09')


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISummer09)
    megrok.pagelet.template('layout.pt')


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISummer09)

    def news(self):
        result = []
        news_edition = asm.cms.edition.select_edition(
            self.application['news'], self.request)
        for item in news_edition.list():
            edition = asm.cms.edition.select_edition(
                item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            result.append(edition)
        result.sort(key=lambda x: x.modified, reverse=True)
        return result[:5]

    def generateCountdown(self):
        times = (('22.01.2010 12:00', True, "until ASSEMBLY!"),
                 ('24.01.2010 18:00', True, "of ASSEMBLY left to enjoy!"),
                  (None, False, "ASSEMBLY is over."),)
        format = '%d.%m.%Y %H:%M'

        now = datetime.datetime.now()

        for (limitString, doCountDown, showString) in times:
            limit = None
            if limitString:
                limit = datetime.datetime.strptime(limitString, format)
            if (not limit) or now < limit:
                if doCountDown:
                    diff = limit - now
                    diff = (diff.days * 24 * 60 * 60) + diff.seconds
                    countdown = ""
                    units = (('years', 31536000), ('months', 2592000),
                             ('days', 86400), ('hours', 3600),
                             ('minutes', 60), ('seconds', 1))
                    messageParts = []
                    for (name, length) in units[:-1]:
                        if diff > length:
                            messageParts.append(
                                '<strong id="clock_%s">%s</strong> %s' %
                                (name, int(diff / length), name))
                            diff = diff % length

                    message = '<span id="clock">%s %s</span>' % (
                        ', '.join(messageParts), showString)
                else:
                    message = showString
                return message

        # This should never get returned...
        return "Welcome to Assembly!"

    # A helper class to get access to the static directory in this module from
    # the layout.

    def render(self):
        return ''


class Navtree(asm.cms.cmsui.Navtree):
    grok.layer(ISummer09)
    grok.context(zope.interface.Interface)

    def update(self):
        self.active = set()
        current = self.context.page
        while current:
            self.active.add(current)
            current = current.__parent__

    def _create_subtree(self, root, levels, output):
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
                sub_tree = self._create_subtree(child, levels-1)
                if sub_tree:
                    tree['subpages'].append(sub_tree)
        if 'active' in tree['class'] and not tree['subpages']:
            tree['class'].add('has_no_children')
        tree['class'] = ' '.join(tree['class'])
        return tree

    def render(self):
        root = self.application
        output = StringIO.StringIO()
        self._create_subtree(root, 3, output)
        return output.getvalue()


class Homepage(asm.cms.Pagelet):
    grok.context(asm.cms.homepage.Homepage)
    grok.name('index')

    def news(self, tag):
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
    grok.layer(ISummer09)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))
