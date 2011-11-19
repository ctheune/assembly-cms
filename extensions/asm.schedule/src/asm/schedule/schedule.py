import BTrees
import StringIO
import asm.cms
import asm.cmsui.tinymce
import asm.cmsui.form
import asm.cmsui.retail
import asm.schedule.interfaces
import asm.workflow.interfaces
import csv
import datetime
import grok
import persistent
import transaction
import zope.interface
from asm.workflow.workflow import WORKFLOW_DRAFT, WORKFLOW_PUBLIC
from asm.schedule.i18n import _, i18n_strftime

class Schedule(asm.cms.Edition):
    """A schedule maintains a list of events and offers a retail UI that
    allows users to efficiently browse the events by filtering and selecting
    specific days and mark past, current and future events visually.
    """

    zope.interface.classProvides(asm.cms.IEditionFactory)

    public_csv = ""
    factory_title = u'Schedule'

    message = None

    def __init__(self):
        super(Schedule, self).__init__()
        self.events = BTrees.IOBTree.IOBTree()

    def copyFrom(self, other):
        super(Schedule, self).copyFrom(other)
        self.events.clear()
        for key, value in other.events.items():
            self.events[key] = value
        self.message = other.message
        self.public_csv = other.public_csv


class TextIndexing(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)

    def __init__(self, schedule):
        result = [schedule.title, schedule.message]
        for event in schedule.events.values():
            result.extend([event.title, event.location])
        result = filter(lambda x: x is not None, result)
        self.body = ' '.join(result)


class SearchPreview(grok.View):

    def update(self, q):
        self.keyword = q
        self.result = []
        for event in self.context.events.values():
            if self.keyword.lower() in event.title.lower():
                self.result.append(event)


class Event(persistent.Persistent):
    """A single event - mostly a data bag."""

    description = u''

    canceled = False

    # Indicates if event is being broadcast on AssemblyTV.
    assemblytv_broadcast = False


class ScheduleUpload(grok.Adapter):
    grok.context(Schedule)
    grok.provides(asm.schedule.interfaces.IScheduleUpload)

    def set_title(self, title):
        self.context.title = title

    def get_title(self):
        return self.context.title

    title = property(fset=set_title, fget=get_title)

    def get_message(self):
        return self.context.message

    def set_message(self, message):
        self.context.message = message

    message = property(get_message, set_message)

    data = None

def get_row_errors(fields, field_data):
    errors = []
    for field in fields:
        if field_data.get(field, None) is None:
            errors.append(u"Field '%s' is missing." % field)


    if None in field_data:
        errors.append(
            "There are extra %d field values with event %s (%s)." % (len(field_data[None]), field_data['id'].decode("utf-8"), field_data['title_en'].decode("utf-8")))
        errors.append(
            u"Make sure that you don't have accidentally pasted text with tab characters to descriptions or titles!")

    for field in ('start_date', 'finish_date'):
        try:
            extract_date(field_data[field])
        except ValueError, e:
            errors.append(
                u"Date string on field '%s' is invalid (%s)." % (field, e))
            errors.append(u"For example date and time 'Saturday 11th of February 2011 18:00' would be 'Sat 12.02.11 18:00'.")

    for field in ('title_fi', 'title_en', 'location_fi', 'location_en'):
        try:
            field_data[field].decode('UTF-8')
        except UnicodeDecodeError, e:
            errors.append(u"Could not decode field '%s' as UTF-8. Make sure that you are sending an UTF-8 encoded file." % field)

    return errors


class Edit(asm.cmsui.form.EditForm):
    """Editing a schedule means uploading a CSV file (as produced by Jussi)
    and updating both language editions from that file.

    It doesn't matter which edition we upload to: we simply put the Finnish
    items into the Finnish edition and work with the English edition
    accordingly.

    """

    form_fields = grok.AutoFields(asm.schedule.interfaces.IScheduleUpload)
    form_fields['message'].custom_widget = asm.cmsui.tinymce.TinyMCEWidget

    @grok.action(u'Upload')
    def upload(self, data=None, title=None, message=None):
        self.context.title = title
        self.context.message = message
        zope.event.notify(grok.ObjectModifiedEvent(self.context))

        if data is None:
            self.flash('Saved changes.')
            return

        if data == "":
            self.flash(u"Empty data file was given!.", "warning")
            return

        page = self.context.page

        finnish = self.context.parameters.replace('lang:*', 'lang:fi')
        finnish = page.getEdition(finnish, create=True)
        finnish.events.clear()

        english = self.context.parameters.replace('lang:*', 'lang:en')
        english = page.getEdition(english, create=True)
        english.events.clear()

        try:
            dialect = csv.Sniffer().sniff(data)
        except csv.Error, e:
            self.flash(u"%s." % e.message, "warning")
            self.flash(u"Make sure that all lines contain the same amount of field delimiter characters.")
            self.flash(u"First row of data: %s" % data.split("\n")[0])
            return
        data = StringIO.StringIO(data)
        fields = ('id', 'outline_number', 'name', 'duration', 'start_date',
                  'finish_date', 'asmtv', 'bigscreen', 'major', 'public',
                  'sumtask', 'class_', 'url', 'title_en', 'title_fi',
                  'location_en', 'location_fi', 'location_url',
                  'outline_level', 'description_en', 'description_fi', 'canceled')
        reader = csv.DictReader(data, fieldnames=fields, dialect=dialect)
        reader = iter(reader)

        # Grab all the public events so that the raw data can be shown.
        public_data = StringIO.StringIO()
        writer = csv.DictWriter(
            public_data,
            fieldnames=fields,
            dialect=dialect,
            quotechar="\\")

        # Ignore the first row
        header = reader.next()
        try:
            writer.writerow(header)
        except ValueError, e:
            # This error comes only when there are too many fields in data.
            field_count = reduce(
                lambda x, y : type(y) == list and x + len(y) or x + 1,
                header.values(),
                0)
            self.flash(u"Data contains %d fields when expecting %d." % (field_count, len(fields)), "warning")
            return

        rows = 0
        for row in reader:
            if row['public'] != 'Yes':
                continue
            errors = get_row_errors(fields, row)
            if len(errors) > 0:
                transaction.abort()
                self.flash(u"Schedule data has an invalid row", "warning")
                for error in errors:
                    self.flash(error, "warning")
                self.flash(row, "warning")
                return
            try:
                writer.writerow(row)
            except ValueError, e:
                transaction.abort()
                self.flash(u"Unexpected error happened (ValueError): %s" % e.message, "warning")
                self.flash(str(row))
                return
            except csv.Error, e:
                transaction.abort()
                self.flash(u"Unexpected error happened (csv.Error): %s" % e.message, "warning")
                self.flash(str(row))
                return
            except TypeError, e:
                transaction.abort()
                self.flash(u"Unexpected error happened (TypeError): %s" % e.message, "warning")
                self.flash(str(row))
                return
            for schedule, lang in [(finnish, 'fi'), (english, 'en')]:
                event = Event()
                event.start = extract_date(row['start_date'])
                event.end = extract_date(row['finish_date'])
                event.major = (row['major'] == 'Yes')
                event.class_ = row['class_'].decode('UTF-8')
                event.url = row['url']
                event.title = row['title_%s' % lang].decode('UTF-8')
                event.location = row['location_%s' % lang].decode('UTF-8')
                event.location_url = row['location_url']
                event.description = row['description_%s' % lang].decode('UTF-8')
                event.canceled = (row['canceled'].lower() == 'yes')
                event.assemblytv_broadcast = (row['asmtv'].lower() == 'yes')
                schedule.events[int(row['id'])] = event
            rows += 1

        public_csv = public_data.getvalue()
        english.public_csv = public_csv
        finnish.public_csv = public_csv
        zope.event.notify(grok.ObjectModifiedEvent(english))
        zope.event.notify(grok.ObjectModifiedEvent(finnish))
        self.flash(u'Your schedule was imported successfully with %d events.' % rows)


@grok.subscribe(asm.workflow.interfaces.PublishedEvent)
def publish_schedule(event):
    # This event listener ensures that the schedule is always published in
    # English and Finnish synchronously.
    if not isinstance(event.draft, Schedule):
        return

    page = event.draft.page

    # We do not know which language the user published because we will be
    # triggered by publishing the other version too. Thus we have to check
    # both possible languages and stop an infinite recursion.
    for lang in ['fi', 'en']:
        public_p = (event.draft.parameters.
                  replace(WORKFLOW_DRAFT, WORKFLOW_PUBLIC).
                  replace('lang:*', 'lang:%s' % lang))

        # We need to publish the draft of this language again, if: no public
        # version exists yet, or the publication date is not the one of the
        # publication that triggered us.
        try:
            public = page.getEdition(public_p)
        except KeyError:
            pass
        else:
            if (public.modified == event.public.modified):
                # The public version is up to date, so we ignore it.
                continue

        # XXX this try-except protects from following case:
        #
        # 1. publish schedule
        # 2. create a draft for one language version
        # 3. publish the draft
        #
        # In step 1 we publish all language versions.
        # In step 2 we create draft for only 1 language version.
        # In step 3 we are in trouble as there is draft only for 1 language.
        try:
            draft = page.getEdition(
                public_p.replace(WORKFLOW_PUBLIC, WORKFLOW_DRAFT))
            asm.workflow.publish(draft, event.public.modified)
        except KeyError:
            pass


def extract_date(date):
    return datetime.datetime.strptime(date, "%a %d.%m.%y %H:%M")

class NullEvent(object):
    end = datetime.datetime(1980, 1, 1)

class FilteredSchedule(object):
    """A helper to create a filtered view on a schedule."""

    filters = {'all': (_('All'), lambda x: True),
               'major': (_('Major'), lambda x: x.major),
               'compo': (_('Compos'),
                         lambda x: x.class_.startswith('Compo'))}

    _last_event = NullEvent()

    def __init__(self, request, schedule, details, day):
        self.request = request
        day_options = set()
        self.details = details
        self.day = day
        by_day = {}
        self.now = datetime.datetime.now()
        matches = self.filters[details][1]

        for key, event in schedule.events.items():
            day_options.add(event.start.date())
            if not matches(event):
                continue
            event_day = event.start.date()
            if day != 'all' and day != event_day:
                continue
            day_events = by_day.setdefault(event_day, [])
            day_events.append(dict(event=event, key=key))

        self.events = []
        for day, events in sorted(by_day.items()):
            if not events:
                continue
            data = {}
            data['day'] = _(day.strftime('%A'))
            hours = {}
            for event in events:
                massaged = dict()
                massaged['classes'] = self.event_class(event['event'])
                massaged['key'] = event['key']
                event = event['event']
                massaged['description'] = event.description
                massaged['title'] = event.title
                massaged['url'] = event.url or None
                massaged['location'] = event.location
                massaged['location_url'] = event.location_url
                massaged['has_until'] = event.start != event.end
                massaged['end_time'] = i18n_strftime(
                    '%H:%M', event.end, self.request)
                massaged['end_day'] = (_(event.end.strftime('%A')+'(until)')
                                       if event.start.day != event.end.day
                                       else u'')
                massaged['canceled'] = event.canceled
                massaged['assemblytv_broadcast'] = event.assemblytv_broadcast
                massaged['major'] = event.major
                hours.setdefault(event.start, []).append(massaged)

            data['hours'] = [dict(hour=i18n_strftime('%H:%M', k, self.request),
                                  events=v) for k,v in
                             sorted(hours.items())]
            self.events.append(data)

        if self.events:
            self._last_event = self.events[-1]

        self.day_options = [
            dict(token=day.isoformat(),
                 class_=(self.day == day and 'selected' or ' '),
                 label=day.strftime('%A'))
            for day in sorted(day_options)]
        self.day_options.insert(0, dict(
            token='all',
            label=_('All'),
            class_=(self.day == 'all' and 'selected' or ' ')))

        self.detail_options = [
            dict(token=key,
                 class_=(self.details == key and 'selected' or ' '),
                 label=value[0])
            for key, value in self.filters.items()]

    def event_class(self, event):
        classes = set([event.class_])
        # self.now < self.last_event.end makes
        if self.now < self._last_event.end and event.end < self.now:
            classes.add('past')
        if event.start > self.now:
            classes.add('future')
        if event.start < self.now and event.end > self.now:
            classes.add('current')
        if event.canceled:
            classes.add('canceled')
        if len(event.description) > 0:
            classes.add('disclose')
        if event.major:
            classes.add('major')
        return ' '.join(classes)


class Index(asm.cmsui.retail.Pagelet):

    def update(self):
        day = self.request.get('day', 'all')
        if day != 'all':
            day = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        details = self.request.get('details', 'all')
        self.filter = FilteredSchedule(
            self.request, self.context, details, day)

    def format_date(self, date):
        specials = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st',
                    22: 'nd', 23: 'rd', 31: 'st'}
        day = '%s%s' % (date.day, specials.get(date.day, 'th'))
        return '%s %s of %s %s' % (date.strftime('%A'), day,
                                   date.strftime('%B'), date.strftime('%Y'))


class Csv(grok.View):
    grok.name('csv')
    grok.context(Schedule)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)

    def render(self):
        return self.context.public_csv
