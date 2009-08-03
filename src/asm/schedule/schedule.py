import BTrees
import StringIO
import asm.cms
import asm.schedule.interfaces
import asm.workflow.interfaces
import csv
import datetime
import grok
import persistent
import time
import zope.interface


class Schedule(asm.cms.Variation):
    """A schedule maintains a list of events and offers a retail UI that
    allows users to efficiently browse the events by filtering and selecting
    specific days and mark past, current and future events visually.
    """

    zope.interface.classProvides(asm.cms.IVariationFactory)

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
    and updating both language variations from that file.

    It doesn't matter which variation we upload to: we simply put the Finnish
    items into the Finnish variation and work with the English variation
    accordingly.

    """

    form_fields = grok.AutoFields(asm.schedule.interfaces.IScheduleUpload)

    @grok.action(u'Upload')
    def upload(self, data):
        location = self.context.__parent__

        parameters = set(self.context.parameters)
        for p in list(parameters):
            if p.startswith('lang:'):
                parameters.remove(p)
        finnish = parameters.copy()
        finnish.add('lang:fi')
        finnish = location.getVariation(finnish, create=True)
        finnish.events.clear()
        english = parameters.copy()
        english.add('lang:en')
        english = location.getVariation(english, create=True)
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
    location = event.draft.__parent__
    parameters = event.public.parameters.remove('lang:*')
    for lang in ['fi', 'en']:
        lang_p = parameters.add('lang:%s' % lang).replace('workflow:draft',
                                                          'workflow:public')

        try:
            public = location.getVariation(p.replace(')
        except KeyError:
            publish = True
        else:
            publish = (public._workflow_publication_date !=
                       event.public._workflow_publication_date)
        if publish:
            p.remove('workflow:public')
            p.add('workflow:draft')
            asm.workflow.workflow.publish(location.getVariation(p),
                                 event.public._workflow_publication_date)


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
