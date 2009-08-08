import BTrees
import StringIO
import asm.cms
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

    def __init__(self):
        super(Schedule, self).__init__()
        self.events = BTrees.IOBTree.IOBTree()

    def copyFrom(self, other):
        self.events.clear()
        for key, value in other.events.items():
            self.events[key] = value


class Event(persistent.Persistent):
    """A single event - mostly a data bag."""


class Edit(asm.cms.Form):
    """Editing a schedule means uploading a CSV file (as produced by Jussi)
    and updating both language editions from that file.

    It doesn't matter which edition we upload to: we simply put the Finnish
    items into the Finnish edition and work with the English edition
    accordingly.

    """

    form_fields = grok.AutoFields(asm.schedule.interfaces.IScheduleUpload)

    @grok.action(u'Upload')
    def upload(self, data):
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
                  'location_en', 'location_fi', 'location_url', 'outline_level') 
        reader = csv.DictReader(data, fieldnames=fields, dialect=dialect)
        for row in reader:
            if row['public'] != 'Yes':
                continue
            for schedule, lang in [(finnish, 'fi',) (english, 'en')]:
                event = Event()
                event.start = extract_date(row['start_date'])
                event.end = extract_date(row['finish_date'])
                event.major = row['major'] == 'Yes'
                event.class_ = row['class_'].decode('UTF-8')
                event.url = row['url']
                event.title = row['title_%s' % lang].decode('UTF-8')
                event.location = row['location_%s' % lang].decode('UTF-8')
                event.location_url = row['location_url']
                schedule.events[int(row['id'])] = event

        self.flash(u'Your schedule was imported successfully.')


@grok.subscribe(asm.workflow.interfaces.PublishedEvent)
def publish_schedule(event):
    # This event listener ensures that the schedule is always published in
    # English and Finnish synchronously.
    if not isinstance(event.draft, Schedule):
        return

    page = self.context.page

    # We do not know which language the user published because we will be
    # triggered by publishing the other version too. Thus we have to check
    # both possible languages and stop an infinite recursion.
    for lang in ['fi', 'en']:
        public_p = (self.context.parameters.
                  replace(WORKFLOW_DRAFT, WORKFLOW_PUBLIC).
                  replace('lang:*', 'lang:%s' % lang))

        # We need to publish the draft of this language again, if: no public
        # version exists yet, or the publication date is not the one of the
        # publication that triggered us.
        try:
            public = page.getEdition(public)
        except KeyError:
            pass
        else:
            if (public.modified == event.public.modified):
                # The public version is up to date, so we ignore it.
                continue

        draft = public.parameters.replace(WORKFLOW_PUBLIC, WORKFLOW_DRAFT)
        draft = page.getEdition(draft)
        asm.workflow.publish(draft, event.public.modified)


def extract_date(date):
    return datetime.datetime.strptime(date, "%a %d.%m.%y %H:%M")


class Index(asm.cms.Page):

    def events(self):
        events = []
        current = dict(date=None)
        for event in sorted(self.context.events.values(), key=lambda x:x.start):
            if event.start.date() != current['date']:
                if current['date']:
                    events.append(current)
                current = dict(date=event.start.date(), events=[])
            current['events'].append(event)
        return events

    def format_date(self, date):
        specials = {1 : 'st', 2 : 'nd', 3 : 'rd', 21: 'st',
                    22: 'nd', 23: 'rd', 31: 'st'}
        day = '%s%s' % (date.day, specials.get(date.day, 'th')) 
        return '%s %s of %s %s' % (date.strftime('%A'), day,
                                   date.strftime('%B'), date.strftime('%Y'))
