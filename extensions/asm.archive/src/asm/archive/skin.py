# -*- coding: utf-8 -*-
# Copyright (c) 2011 Assembly Organizing
# See also LICENSE.txt

import asm.cms
import asm.cmsui.interfaces
import asm.cmsui.retail
import asm.mediagallery.externalasset
import asm.mediagallery.gallery
import asm.mediagallery.interfaces
import email.encoders as email_encoders
import email.Header as email_header
import email.Message as email_message
import grok
import megrok.pagelet
import os.path
import random
import re
import smtplib
import urlparse
import urllib
from zope.app.form.browser.textwidgets import TextWidget
import zope.interface

skin_name = 'asmarchive'
asmarchive = asm.cms.cms.Profile(skin_name)
languages = ['en', 'fi']

class ISkin(asm.cmsui.interfaces.IRetailSkin):
    grok.skin(skin_name)


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)
    megrok.pagelet.template('layout.pt')


class MetadataManager(grok.ViewletManager):
    grok.name('metadata')
    grok.layer(ISkin)
    grok.context(asm.cms.interfaces.IEdition)


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISkin)

    # A helper class to get access to the static directory in this module from
    # the layout.

    def render(self):
        return ''

DEFAULT_YEARS = 10
YEAR_MATCH = re.compile("^\d{4}$")

def select_years(application_subpages, request):
    years = filter(
        lambda x: YEAR_MATCH.match(x.__name__),
        list(application_subpages)
        )
    result = []
    for year_page in years:
        edition = asm.cms.edition.select_edition(year_page, request)
        if isinstance(edition, asm.cms.edition.NullEdition):
            continue
        if edition.tags is not None and 'hide-navigation' in edition.tags:
            continue
        result.append(edition)

    return result


class ViewUtils(object):

    def cut_string(self, data, max_length, max_word_length=23):
        if data is None:
            return None
        words = re.split('(\W+)', data)
        short_words = []
        for word in words:
            while len(word) > max_word_length:
                # U+200B ZERO WIDTH SPACE
                short_words.extend([word[:max_word_length], u"\u200B"])
                word = word[max_word_length:]
            short_words.append(word)
        word_cut_data = u"".join(short_words)
        if len(word_cut_data) <= max_length:
            return word_cut_data
        return word_cut_data[:max_length - 3].strip() + u"\u2026"


class YearlyNavigation(grok.View):
    grok.layer(ISkin)
    grok.context(zope.interface.Interface)

    def update(self):
        self.years = select_years(self.application.subpages, self.request)
        self.current_year = self.get_closest_year()

    def get_closest_year(self):
        closest_page = self.context
        application = asm.cms.get_application(closest_page)
        if closest_page == application:
            return None
        while closest_page.__parent__ != application:
            closest_page = closest_page.__parent__

        return asm.cms.edition.select_edition(closest_page, self.request)

    def get_navigation_limits(self, years, limit=DEFAULT_YEARS):

        if not self.current_year in years:
            return (0, min(limit, len(years)))

        max_selection = min(len(years), limit)
        if self.current_year is not None and YEAR_MATCH.match(self.current_year.page.__name__):
            before = max_selection / 2
            after = max_selection - before - 1

            select_index = years.index(self.current_year)

            # In default we are at the beginning of the year list.
            selection_start = 0
            selection_end = max_selection
            if before < select_index + 1 and after < len(years) - select_index:
                selection_start = select_index - before
                selection_end = select_index + after + 1
            elif len(years) - select_index < max_selection:
                selection_start = len(years) - max_selection
                selection_end = len(years)

            return (selection_start, selection_end)
        else:
            return (0, max_selection)

    def _get_removed_years(self, years, max_remove):
        year_count = len(years)
        try:
            current_year_index = years.index(self.get_closest_year())
        # We are probably on the main page.
        except ValueError, e:
            if year_count < 3:
                return [False] * year_count
            items_left = year_count - max_remove
            if items_left < 2:
                items_left = 2
            return [False] * items_left + [True] * (year_count - items_left)

        # Create a list of years that we can remove when moving into mobile mode.
        distances = [abs(index - current_year_index)
                     for index in range(year_count)]
        remove_years = [False] * year_count
        removed_count = 0
        remove_value = max(distances)
        while removed_count < max_remove and remove_value > 1:
            for i in range(year_count):
                if distances[i] == remove_value:
                    remove_years[i] = True
                    removed_count += 1
                if removed_count >= max_remove:
                    break
            remove_value -= 1

        return remove_years

    def list_years_near_current_page(self, limit=DEFAULT_YEARS, max_remove=0):
        assert limit > 2, "Limit must enable navigating back and forth."

        year_start, year_end = self.get_navigation_limits(self.years, limit)

        years = self.years[year_start:year_end]

        remove_years = self._get_removed_years(years, max_remove)

        return [{'year': year, 'remove': remove}
                for year, remove in zip(years, remove_years)]


@grok.subscribe(asm.cms.interfaces.IContentImported)
def generate_map(event):
    # Ensure we only operate on archive sites
    if asmarchive not in event.site.getSiteManager().__bases__:
        return
    years = filter(
        lambda x: YEAR_MATCH.match(x.__name__),
        list(event.site.subpages))
    for homepage in event.site.editions:
        map = {}
        for year in years:
            year_name = year.page.__name__
            map[year_name] = {}
            iids = zope.component.getUtility(zope.intid.IIntIds)
            for category in year.page.subpages:
                map[year_name][category.__name__] = []
                for media in category.subpages:
                    if media.type not in [
                        'asset', asm.mediagallery.externalasset.TYPE_EXTERNAL_ASSET]:
                        continue
                    try:
                        edition = media.getEdition(homepage.parameters)
                    except KeyError:
                        continue
                    asset_edition_id = iids.getId(edition)
                    thumbnail_page = edition.page.get('thumbnail', None)
                    # Assume that this thumbnail has something to do with music.
                    if thumbnail_page is None:
                        thumbnail_page = year['music-thumbnail']

                    thumbnail_edition = thumbnail_page.getEdition(homepage.parameters)
                    thumbnail_edition_id = iids.getId(thumbnail_edition)

                    if thumbnail_page.get('_datauri', None) is None:
                        thumbnail_page['_datauri'] = asm.cms.interfaces.IDataUri(thumbnail_edition)

                    info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)
                    map[year_name][category.__name__].append(
                        (asset_edition_id, info, thumbnail_edition_id))
                if not map[year_name][category.__name__]:
                    del map[year_name][category.__name__]
        homepage.gallery_map = map


class Homepage(asm.cmsui.retail.Pagelet, ViewUtils):

    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('index')

    @property
    def years(self):
        return select_years(self.application.subpages, self.request)

    def editioned_subpages(self, root):
        for page in root.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition

    def select_random_items(self, year, limit=None):
        if not hasattr(self.context, 'gallery_map'):
            raise StopIteration
        result = []
        year_name = year.page.__name__
        for category_items in self.context.gallery_map.get(year_name, {}).values():
            random.shuffle(category_items)
            result.extend(category_items[:limit])
        random.shuffle(result)
        result = result[:limit]
        iids = zope.component.getUtility(zope.intid.IIntIds)
        for asset_edition_id, info, thumbnail_edition_id in result:
            edition = iids.getObject(asset_edition_id)
            thumbnail_edition = iids.getObject(thumbnail_edition_id)
            thumbnail_datauri = thumbnail_edition.page['_datauri']
            yield dict(edition=edition,
                       gallery=info,
                       thumbnail=thumbnail_datauri.datauri)

    @property
    def description(self):
        if 'welcome-message' in self.application:
            edition = asm.cms.edition.select_edition(
                self.application['welcome-message'], self.request)
            return edition
        else:
            return None

class SelectLanguage(grok.View):

    grok.context(zope.interface.Interface)
    grok.name('select-language')
    grok.layer(ISkin)

    def update(self, lang):
        self.request.response.setCookie('asm.translation.lang', lang, path='/')

    def render(self):
        self.redirect(self.url(self.context))


class GalleryIndex(asm.mediagallery.gallery.Index, ViewUtils):

    grok.layer(ISkin)
    grok.context(asm.mediagallery.interfaces.IMediaGallery)
    grok.name('index')

    ITEMS_PER_PAGE = 30

    sort_items = False

    def render_parent(self):
        return asm.mediagallery.gallery.Index.template.render(self)

    def list_categories(self):
        for category in super(GalleryIndex, self).list_categories():
            yield {
                'edition': category,
                'gallery': asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(category),
                }

    @property
    def title(self):
        parent_edition = asm.cms.edition.select_edition(
            self.context.__parent__.__parent__, self.request)
        if asm.mediagallery.interfaces.IMediaGallery.providedBy(parent_edition):
            return u"%s / %s" % (parent_edition.title, self.context.title)
        return self.context.title

    def _add_thumbnail_to_gallery_items(self, items):
        music_thumbnail = None
        parent = self.context.page
        while parent != self.application:
            if 'music-thumbnail' in parent:
                music_thumbnail = parent['music-thumbnail']
                break
            parent = parent.__parent__
        item_list = list(items)
        for item in item_list:
            if 'thumbnail' in item['edition'].page:
                item['thumbnail'] = item['edition'].page['thumbnail']
            elif music_thumbnail is not None:
                item['thumbnail'] = music_thumbnail
            else:
                item['thumbnail'] = None
        return item_list

    def list_category_items(self, *args, **kw):
        items = super(GalleryIndex, self).list_category_items(*args, **kw)
        return self._add_thumbnail_to_gallery_items(items)

    def list_items(self, *args, **kw):
        items = super(GalleryIndex, self).list_items(*args, **kw)
        return self._add_thumbnail_to_gallery_items(items)

def get_party_name(year, category):
    if year < 2007:
        return u"Assembly %d" % year
    elif 'winter' in category.__name__:
        return u"Assembly Winter %d" % year
    else:
        return u"Assembly Summer %d" % year


class ExternalAssetIndex(asm.mediagallery.externalasset.Index, ViewUtils):
    grok.layer(ISkin)
    grok.context(asm.mediagallery.interfaces.IExternalAsset)
    grok.name('index')

    @property
    def current_url_escaped(self):
        return urllib.quote_plus(self.url(self.context))

    @property
    def title(self):
        title = self.context.title
        party_year = int(self.context.__parent__.__parent__.__parent__.__name__)
        category = self.context.__parent__.__parent__
        category_edition = asm.cms.edition.select_edition(
            category, self.request)
        party_name = get_party_name(party_year, category)
        if 'assemblytv' in category.__name__ or \
                'seminar' in category.__name__ or \
                'winter' in category.__name__:
            return u"%s / %s / %s" % (title, party_name, category_edition.title)
        author = self.info.author
        return u"%s by %s" % (title, author)

    def update(self):
        super(ExternalAssetIndex, self).update()
        self.info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(self.context)


class ExternalAssetMetadata(grok.Viewlet):
    grok.viewletmanager(MetadataManager)
    grok.context(asm.mediagallery.interfaces.IExternalAsset)
    grok.view(ExternalAssetIndex)

    def application_title(self):
        edition = asm.cms.edition.select_edition(self.view.application, self.request)
        return edition.title

    def description(self):
        party_year = int(self.context.__parent__.__parent__.__parent__.__name__)
        category = self.context.__parent__.__parent__
        category_edition = asm.cms.edition.select_edition(
            category, self.request)

        party_name = get_party_name(party_year, category)

        category_description = None
        if 'assemblytv' in category.__name__ or 'winter' in category.__name__:
            category_description = u"AssemblyTV program"
        elif 'seminar' in category.__name__:
            category_description = u"seminar"
        else:
            category_description = u"%s competition entry" % category_edition.title

        base_description = self.view.info.description
        if base_description is None:
            return None
        description = re.sub("<[^>]+>", "", base_description)
        description = re.sub("\nTitle:.+", "", description)
        description = re.sub("\nAuthor:.+", "", description)
        description = re.sub("\n+", " ", description)
        description = re.sub(" +", " ", description)
        full_description = u"%s %s. %s" % (party_name, category_description, description)
        return full_description.strip()



class GalleryNavBar(asm.mediagallery.gallery.GalleryNavBar, ViewUtils):
    grok.layer(ISkin)
    grok.context(asm.cms.interfaces.IEdition)

    def _return_same_type_page(self, page):
        if not page:
            return None
        if page.page.type != self.context.page.type:
            return None
        return page

    def next(self):
        next_page = self._return_same_type_page(super(GalleryNavBar, self).next())
        if next_page is None:
            return None
        if next_page.tags is not None and 'hide-navigation' in next_page.tags:
            return None
        return next_page

    def previous(self):
        prev_page = self._return_same_type_page(super(GalleryNavBar, self).previous())
        if prev_page is None:
            return None
        if prev_page.tags is not None and 'hide-navigation' in prev_page.tags:
            return None
        return prev_page


class GalleryBreadCrumbs(grok.View):
    grok.layer(ISkin)
    grok.context(asm.cms.interfaces.IEdition)
    def update(self):
        pages = []
        page = self.context.page
        while not isinstance(page, asm.cms.cms.CMS):
            pages.insert(0, asm.cms.edition.select_edition(page, self.request))
            page = page.__parent__
        self.breadcrumbs = pages[0:-1]


class DownloadDomain(grok.View):
    grok.layer(ISkin)
    grok.context(unicode)
    grok.name("downloaddomain")

    def render(self):
        address = re.sub(""".+href="([^"]+?)".+""", "\\1", self.context)
        return urlparse.urlparse(address).netloc


class IFeedbackForm(zope.interface.Interface):

    page = zope.schema.TextLine(title=u'The page feedback is about',
                                required=False)
    message = zope.schema.Text(title=u'Feedback message')

    name = zope.schema.TextLine(title=u'Your name', required=False)
    email = zope.schema.TextLine(title=u'Email address',
                                 required=False,
                                 constraint=re.compile("@").search)

def get_specific_width_text_widget(size):
    class LongTextWidget(TextWidget):
        displayWidth = size
    return LongTextWidget

class Feedback(asm.cmsui.form.Form):
    grok.require('zope.Public')
    grok.layer(ISkin)
    grok.context(asm.cms.homepage.Homepage)

    title = u"Feedback"

    form_fields = grok.AutoFields(IFeedbackForm)

    form_fields['page'].custom_widget = get_specific_width_text_widget(70)
    form_fields['name'].custom_widget = get_specific_width_text_widget(40)
    form_fields['email'].custom_widget = get_specific_width_text_widget(40)

    # This field is not visible for normal browser users.
    form_fields += grok.Fields(
        **{'honeypot': zope.schema.TextLine(title=u'Honeypot', description=u"You should not see this field. Do not fill it.", required=False)})
    class HoneyPotWidget(TextWidget):
        cssClass = 'honeypot'
    form_fields['honeypot'].custom_widget = HoneyPotWidget

    template = grok.PageTemplateFile(os.path.join("templates", "form.pt"))
    prefix = ''

    mail_template = u'''Assembly Archive feedback.

From: %(name)s <%(email)s>
Page: %(page)s <%(root)s/%(page)s>

---- feedback starts ----
%(message)s
---- feedback ends ----

'''

    smtp_host = "mail.assembly.org"
    target_address = "web-dev<>assembly.org".replace("<>", "@")

    @grok.action(u'Send feedback')
    def send(self, message, page=None, name=None, email=None, honeypot=None):
        # Detect if a spambot has just filled all form fields.
        if honeypot is not None:
            self.redirect(self.url('feedback-accepted-honeypot'))
            return

        page = page or u""
        name = name or u"UNKNOWN"
        email = email or u"EMPTY-EMAIL"
        message_body = self.mail_template % dict(
                message=message,
                page=page,
                name=name,
                email=email,
                root=self.application_url(),
                )

        message = email_message.Message()
        message.set_payload(message_body.encode('utf-8'))

        subject_header = email_header.Header(
            (u'Assembly Archive feedback about "%s"' % page).encode('utf-8'),
            'utf-8')
        message['Subject'] = subject_header

        message['To'] = self.target_address

        from_header = email_header.Header(
            (u'%s <%s>' % (name, email)).encode('utf-8'),
            'utf-8')
        message['From'] = from_header

        email_encoders.encode_quopri(message)
        message.set_charset('utf-8')
        message_str = message.as_string()
        smtp = smtplib.SMTP(self.smtp_host)
        smtp.sendmail(self.target_address, [self.target_address], message_str)
        self.flash(u'Your feedback was accepted.')
        self.redirect(self.url('feedback-accepted'))


class FeedbackAccepted(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('feedback-accepted')


class FeedbackAcceptedHoneypot(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.homepage.Homepage)
    grok.layer(ISkin)
    grok.name('feedback-accepted-honeypot')
