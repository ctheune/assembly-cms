import asm.cms
import asm.cmsui.retail
import asm.cmsui.interfaces
import datetime
import grok
import megrok.pagelet
import zope.interface
from asm.schedule.i18n import i18n_strftime
from asm.summer11mini.i18n import _

summer11mini = asm.cms.cms.Profile('summer11mini')
languages = ['en', 'fi']
skin_name = 'summer11mini'


class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin('summer11mini')


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    @property
    def schedule(self):
        if 'program' not in self.application or 'schedule' not in self.application['program']:
            raise StopIteration()
        return asm.cms.edition.select_edition(
            self.application['program']['schedule'], self.request)

    def event_data(self, key, event):
        url = '%s#%s' % (self.url(self.application['program']['schedule']), key)
        start = i18n_strftime('%H:%M', event.start, self.request)
        end = i18n_strftime('%H:%M', event.end, self.request)
        return dict(event=event, key=key, url=url, start=start, end=end)

    @property
    def current_events(self):
        result = []
        now = datetime.datetime.now()
        for key, event in self.schedule.events.items():
            if event.start <= now and event.end > now:
                result.append(self.event_data(key, event))
        return result

    @property
    def upcoming_events(self):
        result = []
        now = datetime.datetime.now()
        horizon = now + datetime.timedelta(seconds=3600)
        for key, event in self.schedule.events.items():
            if event.start <= horizon and event.start > now:
                result.append(self.event_data(key, event))
        return result


    def news(self):
        try:
            # This try/except block makes the skin more resilient towards
            # incomplete data and use with databases that don't exactly fit
            # the expected content model.
            result = []
            news_edition = asm.cms.edition.select_edition(
                self.application['news'], self.request)
            for item in news_edition.list():
                edition = asm.cms.edition.select_edition(
                    item, self.request)
                if isinstance(edition, asm.cms.edition.NullEdition):
                    continue
                result.append(edition)
            result.sort(key=lambda x: x.created, reverse=True)
            return result[:5]
        except:
            return []

    def generateCountdown(self):
        times = (('04.08.2011 12:00', True, _("until ASSEMBLY!")),
                 ('07.08.2011 18:00', True, _("of ASSEMBLY left to enjoy!")),
                  (None, False, _("ASSEMBLY is over.")),)
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
                    units = ((_('years'), 31536000), (_('months'), 2592000),
                             (_('days'), 86400), (_('hours'), 3600),
                             (_('minutes'), 60), (_('seconds'), 1))
                    messageParts = []
                    for (name, length) in units[:-1]:
                        if diff > length:
                            messageParts.append(
                                '<strong id="clock_%s">%s</strong> %s' %
                                (name, int(diff / length),
                                 zope.i18n.translate(name,
                                                     context=self.request)))
                            diff = diff % length

                    message = '<span id="clock">%s %s</span>' % (
                        ', '.join(messageParts),
                        zope.i18n.translate(showString, context=self.request))
                else:
                    message = zope.i18n.translate(showString,
                                                  context=self.request)
                return message

        # This should never get returned...
        return zope.i18n.translate(
            _("Welcome to Assembly!"), context=self.request)

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

    def news(self, tag=None):
        if 'news' not in self.context.page:
           raise StopIteration()

        news_edition = asm.cms.edition.select_edition(
            self.context.page['news'], self.request)
        for item in news_edition.list():
            edition = asm.cms.edition.select_edition(
                item, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            if tag is not None and not edition.has_tag(tag):
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
                      key=lambda x: x['edition'].created,
                      reverse=True)

    def frontpage(self):
        return list(sorted(self.news(),
                           key=lambda x: x['edition'].created,
                           reverse=True))[:12]


class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))
