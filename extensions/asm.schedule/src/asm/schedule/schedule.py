import BTrees
import StringIO
import asm.cms
import asm.cms.tinymce
import asm.schedule.interfaces
import asm.workflow.interfaces
import csv
import datetime
import grok
import persistent
import zope.interface
from asm.workflow.workflow import WORKFLOW_DRAFT, WORKFLOW_PUBLIC


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


class TextIndexing(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)

    def __init__(self, schedule):
        result = [schedule.title, schedule.message]
        for event in schedule.events.values():
            result.extend([event.title, event.location])
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


class Edit(asm.cms.EditForm):
    """Editing a schedule means uploading a CSV file (as produced by Jussi)
    and updating both language editions from that file.

    It doesn't matter which edition we upload to: we simply put the Finnish
    items into the Finnish edition and work with the English edition
    accordingly.

    """

    form_fields = grok.AutoFields(asm.schedule.interfaces.IScheduleUpload)
    form_fields['message'].custom_widget = asm.cms.tinymce.TinyMCEWidget

    @grok.action(u'Upload')
    def upload(self, data=None, title=None, message=None):
        self.context.title = title
        self.context.message = message
        zope.event.notify(grok.ObjectModifiedEvent(self.context))
        
        if not data:
            self.flash('Saved changes.')
            return
        page = self.context.page

        finnish = self.context.parameters.replace('lang:*', 'lang:fi')
        finnish = page.getEdition(finnish, create=True)
        finnish.events.clear()

        english = self.context.parameters.replace('lang:*', 'lang:en')
        english = page.getEdition(english, create=True)
        english.events.clear()

        dialect = csv.Sniffer().sniff(data)
        data = StringIO.StringIO(data)
        fields = ('id', 'outline_number', 'name', 'duration', 'start_date',
                  'finish_date', 'asmtv', 'bigscreen', 'major', 'public',
                  'sumtask', 'class_', 'url', 'title_en', 'title_fi',
                  'location_en', 'location_fi', 'location_url',
                  'outline_level')
        reader = csv.DictReader(data, fieldnames=fields, dialect=dialect)
        reader = iter(reader)

        # Grab all the public events so that the raw data can be shown.
        public_data = StringIO.StringIO()
        writer = csv.DictWriter(public_data, fieldnames=fields, dialect=dialect)

        # Ignore the first row
        header = reader.next()
        writer.writerow(header)

        for row in reader:
            if row['public'] != 'Yes':
                continue
            writer.writerow(row)
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
                schedule.events[int(row['id'])] = event

        public_csv = public_data.getvalue()
        english.public_csv = public_csv
        finnish.public_csv = public_csv
        zope.event.notify(grok.ObjectModifiedEvent(english))
        zope.event.notify(grok.ObjectModifiedEvent(finnish))
        self.flash(u'Your schedule was imported successfully.')


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

        draft = page.getEdition(public_p.replace(WORKFLOW_PUBLIC,
                                                 WORKFLOW_DRAFT))
        asm.workflow.publish(draft, event.public.modified)


def extract_date(date):
    return datetime.datetime.strptime(date, "%a %d.%m.%y %H:%M")


class FilteredSchedule(object):
    """A helper to create a filtered view on a schedule."""

    filters = {'all': ('all events', lambda x: True),
               'major': ('major events only', lambda x: x.major),
               'compo': ('compo-related events',
                         lambda x: x.class_.startswith('Compo'))}

    def __init__(self, schedule, details, day):
        day_options = set()
        self.details = details
        self.day = day

        by_day = {}
        matches = self.filters[details][1]

        for event in schedule.events.values():
            day_options.add(event.start.date())
            if not matches(event):
                continue
            event_day = event.start.date()
            if day != 'all' and day != event_day:
                continue
            day_events = by_day.setdefault(event_day, [])
            day_events.append(event)

        self.events = []
        for day, events in sorted(by_day.items()):
            if not events:
                continue
            data = {}
            data['day'] = day
            hours = {}
            for event in events:
                hours.setdefault(event.start, []).append(event)
            data['hours'] = [dict(hour=k, events=v) for k,v in
                             sorted(hours.items())]
            self.events.append(data)

        self.day_options = [
            dict(token=day.isoformat(),
                 class_=(self.day == day and 'selected' or ' '),
                 label=day.strftime('%A'))
            for day in sorted(day_options)]
        self.day_options.append(dict(
            token='all',
            label='all days',
            class_=(self.day == 'all' and 'selected' or ' ')))

        self.detail_options = [
            dict(token=key,
                 class_=(self.details == key and 'selected' or ' '),
                 label=value[0])
            for key, value in self.filters.items()]


class Index(asm.cms.Pagelet):

    def update(self):
        day = self.request.get('day', 'all')
        if day != 'all':
            day = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        details = self.request.get('details', 'all')
        self.now = datetime.datetime.now()

        self.filter = FilteredSchedule(
            self.context, details, day)

    def event_class(self, event):
        if event.end < self.now:
            return 'past'
        if event.start > self.now:
            return 'future'
        if event.start < self.now and event.end > self.now:
            return 'current'

    def format_date(self, date):
        specials = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st',
                    22: 'nd', 23: 'rd', 31: 'st'}
        day = '%s%s' % (date.day, specials.get(date.day, 'th'))
        return '%s %s of %s %s' % (date.strftime('%A'), day,
                                   date.strftime('%B'), date.strftime('%Y'))


class Csv(grok.View):
    grok.name('csv')
    grok.context(Schedule)
    grok.layer(asm.cms.interfaces.IRetailSkin)

    def render(self):
        return self.context.public_csv
