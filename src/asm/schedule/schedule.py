import BTrees
import StringIO
import asm.cms.form
import asm.cms.interfaces
import asm.cms.location
import asm.schedule.interfaces
import csv
import datetime
import grok
import megrok.pagelet
import persistent
import time
import zope.interface


def extract_date(date):
    return datetime.datetime.strptime(date, "%a %d.%m.%y %H:%M")


class Schedule(asm.cms.location.Variation):

    zope.interface.classProvides(asm.cms.interfaces.IVariationFactory)

    def __init__(self):
        super(Schedule, self).__init__()
        self.events = BTrees.IOBTree.IOBTree()

    def copyFrom(self, other):
        self.events.clear()
        for key, value in other.events.items():
            self.events[key] = value


class Edit(asm.cms.form.Form):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('index')

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
            event_fi = Event()
            event_fi.start = extract_date(row['start_date'])
            event_fi.end = extract_date(row['finish_date'])
            event_fi.major = row['major'] == 'Yes'
            event_fi.class_ = row['class_'].decode('UTF-8')
            event_fi.url = row['url']
            event_fi.title = row['title_fi'].decode('UTF-8')
            event_fi.location = row['location_fi'].decode('UTF-8')
            event_fi.location_url = row['location_url']
            finnish.events[int(row['id'])] = event_fi
            
            event_en = Event()
            event_en.start = extract_date(row['start_date'])
            event_en.end = extract_date(row['finish_date'])
            event_en.major = row['major'] == 'Yes'
            event_en.class_ = row['class_'].decode('UTF-8')
            event_en.url = row['url']
            event_en.title = row['title_en'].decode('UTF-8')
            event_en.location = row['location_en'].decode('UTF-8')
            event_en.location_url = row['location_url']
            english.events[int(row['id'])] = event_en

        self.flash(u'Schedule imported')


class Event(persistent.Persistent):
    pass


class Index(megrok.pagelet.Pagelet):
    grok.layer(asm.cms.interfaces.IRetailSkin)

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
        specials = { 1 : 'st', 2 : 'nd', 3 : 'rd', 21: 'st',
                22: 'nd', 23: 'rd', 31: 'st', }
        day = '%s%s' % (date.day, specials.get(date.day, 'th')) 
        return '%s %s of %s %s' % (date.strftime('%A'), day,
                                   date.strftime('%B'), date.strftime('%Y'))
 
