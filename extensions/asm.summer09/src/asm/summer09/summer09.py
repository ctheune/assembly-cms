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

    def generateCountdown(dummy):
        #request = container.REQUEST
        #RESPONSE =  request.RESPONSE

        # time ( YYYY-MM-DDThh:ss:mmTZD or None), boolean for countdown,
        # string to show
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
                'active': False,
                'subpages': []}
        if root in self.active:
            tree['active'] = True
            for child in root.subpages:
                sub_tree = self._create_subtree(child, levels-1)
                if sub_tree:
                    tree['subpages'].append(sub_tree)
        return tree

    def tree(self):
        root = self.application

        tree = self._create_subtree(root, 3)
        return tree['subpages']


class Homepage(asm.cms.Pagelet):
    grok.context(asm.cms.homepage.Homepage)
    grok.name('index')

    def news(self, tag):
        news_edition = asm.cms.edition.select_edition(
            self.context.page['news2'], self.request)
        for item in news_edition.list():
            edition = asm.cms.edition.select_edition(
                item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            if not edition.has_tag(tag):
                continue
            yield edition

    def featured(self):
        return self.news('featured')

    def big_news(self):
        return list(self.news('frontpage'))[:4]

    def small_news(self):
        return list(self.news('frontpage'))[4:12]
