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
import json
import persistent
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
    public_json = ""
    factory_title = u'Schedule'

    message = None
    locations = None

    def __init__(self):
        super(Schedule, self).__init__()
        self.events = BTrees.IOBTree.IOBTree()
        self.locations = BTrees.OOBTree.OOBTree()

    def copyFrom(self, other):
        super(Schedule, self).copyFrom(other)
        self.events.clear()
        for key, value in other.events.items():
            self.events[key] = value
        self.locations.clear()
        for key, value in other.locations.items():
            self.locations[key] = value
        self.message = other.message
        self.public_csv = other.public_csv
        self.public_json = other.public_json


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

    location_id = None
    location = ""
    location_url = ""


class Location(persistent.Persistent):
    """A single location."""


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

    if len(errors) > 0:
        return errors

    if None in field_data:
        errors.append(
            "There are extra %d field values with event %s (%s)." %
            (len(field_data[None]), field_data['id'].decode("utf-8"),
             field_data['title_en'].decode("utf-8")))
        errors.append(
            u"Make sure that you don't have accidentally pasted text "
            u"with tab characters to descriptions or titles!")

    for field in ('start_date', 'finish_date'):
        try:
            extract_date_oldcsv(field_data[field])
        except ValueError, e:
            errors.append(
                u"Date string on field '%s' is invalid (%s)." % (field, e))
            errors.append(
                u"For example date and time 'Saturday 11th of February 2011 "
                u"18:00' would be 'Sat 12.02.11 18:00'.")

    for field in ('title_fi', 'title_en', 'location_fi', 'location_en'):
        try:
            field_data[field].decode('UTF-8')
        except UnicodeDecodeError, e:
            errors.append(
                u"Could not decode field '%s' as UTF-8. Make sure that you "
                u"are sending an UTF-8 encoded file." % field)

    return errors


def get_row_errors_new(fields, field_data):
    errors = []
    for field in fields:
        if field_data.get(field, None) is None:
            errors.append(u"Field '%s' is missing." % field)

    if len(errors) > 0:
        return errors

    if None in field_data:
        errors.append(
            "There are extra %d field values with event %s (%s)." %
            (len(field_data[None]), field_data['id'].decode("utf-8"),
             field_data['title_en'].decode("utf-8")))
        errors.append(
            u"Make sure that you don't have accidentally pasted text "
            u"with tab characters to descriptions or titles!")

    for field in ('start_date', 'finish_date'):
        try:
            extract_date_newcsv(field_data[field])
        except ValueError, e:
            errors.append(
                u"Date string on field '%s' is invalid (%s)." % (field, e))
            errors.append(
                u"For example date and time 'Saturday 11th of February 2011 "
                u"18:00' would be '12.02.11 18:00'.")

    for field in ('title_fi', 'title_en'):
        try:
            field_data[field].decode('UTF-8')
        except UnicodeDecodeError, e:
            errors.append(
                u"Could not decode field '%s' as UTF-8. Make sure that you "
                u"are sending an UTF-8 encoded file." % field)

    return errors


class InvalidParserError(RuntimeError):
    pass


class ScheduleImportError(RuntimeError):
    def __init__(self, messages):
        self.messages = messages


class CsvWriter(object):
    result_fields = ('id', 'outline_number', 'name', 'duration', 'start_date',
                     'finish_date', 'asmtv', 'bigscreen', 'major', 'public',
                     'sumtask', 'class_', 'url', 'title_en', 'title_fi',
                     'location_en', 'location_fi', 'location_url',
                     'outline_level', 'description_en', 'description_fi',
                     'canceled')

    def __init__(self):
        self.data_stream = StringIO.StringIO()
        self.writer = csv.DictWriter(
            self.data_stream,
            fieldnames=self.result_fields,
            quotechar="\\",
            delimiter='\t')
        self.writer.writerow(dict(zip(self.result_fields, self.result_fields)))

    def getCsv(self):
        return self.data_stream.getvalue()

    def __call__(self, event_id, event_en, event_fi):
        row = {
            'id': event_id,
            'outline_number': 0,
            'name': "NA",
            'duration': "NA",
            'start_date': format_date(event_en.start),
            'finish_date': format_date(event_en.end),
            'asmtv': event_en.assemblytv_broadcast and "yes" or "no",
            'bigscreen': "no",
            'major': event_en.major and "yes" or "no",
            'public': "yes",
            'sumtask': "no",
            'class_': event_en.class_,
            'url': event_en.url,
            'title_en': event_en.title.encode("utf-8"),
            'title_fi': event_fi.title.encode("utf-8"),
            'location_en': event_en.location.encode("utf-8"),
            'location_fi': event_fi.location.encode("utf-8"),
            'location_url': event_en.location_url,
            'outline_level': "NA",
            'description_en': event_en.description.encode("utf-8"),
            'description_fi': event_fi.description.encode("utf-8"),
            'canceled': event_en.canceled and "yes" or "no"
            }
        self.writer.writerow(row)


def get_csv_reader(string_data, data_identifier, expected_fields):
    sniff_data = string_data[:50]
    if ";" not in sniff_data and "\t" not in sniff_data:
        raise InvalidParserError()
    lines = string_data.split("\n")
    if data_identifier not in lines[0].lower():
        raise InvalidParserError()
    try:
        dialect = csv.Sniffer().sniff(string_data)
    except csv.Error, e:
        messages = [
            (u"%s." % e.message, "warning"),
            (u"Make sure that all lines contain the same number of field "
             u"delimiter characters.",),
            (u"First row of data: %s" % string_data.split("\n")[0],),
            ]
        raise ScheduleImportError(messages)

    data = StringIO.StringIO(string_data)

    reader = csv.DictReader(data, fieldnames=expected_fields, dialect=dialect)
    reader = iter(reader)
    return reader


def parse_newcsv(context, string_data):
    fields = ("id", "name", "duration", "start_date", "finish_date",
              "asmtv", "bigscreen", "major", "public", "onsite", "sumtask",
              "category", "subcategory", "url", "title_en", "title_fi",
              "location_id", "canceled")

    reader = get_csv_reader(string_data, "subcategory", fields)

    if "\n" not in string_data:
        messages = [
            (u"Schedule data is in invalid format: no newline characters in the file.", "warning")
            ]
        raise ScheduleImportError(messages)

    # Ignore the first row
    try:
        reader.next()
    except csv.Error as e:
        messages = [
            (u"Schedule data is in invalid format", "warning"),
            (e.message, "warning")
            ]
        raise ScheduleImportError(messages)

    finnish = {}
    english = {}

    for row in reader:
        if row['public'] != 'Yes':
            continue
        errors = get_row_errors_new(fields, row)
        if len(errors) > 0:
            messages = [
                (u"Schedule data has an invalid row", "warning")
                ]
            for error in errors:
                messages.append((error, "warning"))
                messages.append((row, "warning"))
            raise ScheduleImportError(messages)
        item_id = None
        try:
            item_id = int(row['id'])
        except ValueError:
            messages = [
                (u"Row ID '%s' was not numeric." % row['id'], "warning"),
                (str(row),)
                ]
            raise ScheduleImportError(messages)
        for events, lang in [(finnish, 'fi'), (english, 'en')]:
            event = Event()
            event.start = extract_date_newcsv(row['start_date'])
            event.end = extract_date_newcsv(row['finish_date'])
            event.major = (row['major'].lower() == 'yes')
            event.class_ = "%s_%s" % (
                row['category'].decode('UTF-8'),
                row['subcategory'].decode('UTF-8'))
            event.url = row['url']
            event.title = row['title_%s' % lang].decode('UTF-8')
            event.location_id = row['location_id']
            event.canceled = (row['canceled'].lower() == 'yes')
            event.assemblytv_broadcast = (row['asmtv'].lower() == 'yes')
            events[item_id] = event

    return {
        'type': 'events',
        "finnish": finnish,
        "english": english
        }


def parse_csv(context, string_data):
    fields = ('id', 'outline_number', 'name', 'duration', 'start_date',
              'finish_date', 'asmtv', 'bigscreen', 'major', 'public',
              'sumtask', 'class_', 'url', 'title_en', 'title_fi',
              'location_en', 'location_fi', 'location_url',
              'outline_level', 'description_en', 'description_fi', 'canceled')
    reader = get_csv_reader(string_data, "outline_number", fields)

    # Ignore the first row
    reader.next()

    finnish = {}
    english = {}

    for row in reader:
        if row['public'] != 'Yes':
            continue
        errors = get_row_errors(fields, row)
        if len(errors) > 0:
            messages = [
                (u"Schedule data has an invalid row", "warning")
                ]
            for error in errors:
                messages.append((error, "warning"))
                messages.append((row, "warning"))
            raise ScheduleImportError(messages)
        item_id = None
        try:
            item_id = int(row['id'])
        except ValueError:
            messages = [
                (u"Row ID '%s' was not numeric." % row['id'], "warning"),
                (str(row),)
                ]
            raise ScheduleImportError(messages)
        for events, lang in [(finnish, 'fi'), (english, 'en')]:
            event = Event()
            event.start = extract_date_oldcsv(row['start_date'])
            event.end = extract_date_oldcsv(row['finish_date'])
            event.major = (row['major'] == 'Yes')
            event.class_ = row['class_'].decode('UTF-8')
            event.url = row['url']
            event.title = row['title_%s' % lang].decode('UTF-8')
            event.location = row['location_%s' % lang].decode('UTF-8')
            event.location_url = row['location_url']
            event.description = row['description_%s' % lang].decode('UTF-8')
            event.canceled = (row['canceled'].lower() == 'yes')
            event.assemblytv_broadcast = (row['asmtv'].lower() == 'yes')
            events[item_id] = event

    return {
        'type': 'events',
        "finnish": finnish,
        "english": english
        }


def parse_json(context, data):
    data_dict = None
    try:
        data_dict = json.loads(data)
    except ValueError:
        raise InvalidParserError()

    locations = {'fi': {}, 'en': {}}
    for location_id, location in data_dict['locations'].items():
        location_en = {
            'name': location.get('name', ""),
            'description': location.get('description', ""),
            'url': location.get('link', "")
            }
        locations['en'][location_id] = location_en
        location_fi = {
            'name': location.get('name_fi') or location_en['name'],
            'description': location.get('description_fi') or
                location_en['description'],
            'url': location.get('link_fi') or location_en.get('link', "")
            }
        locations['en'][location_id] = location_en
        locations['fi'][location_id] = location_fi

    events = {'fi': {}, 'en': {}}
    for language, postfix in [('en', ''), ('fi', '_fi')]:
        for event in data_dict['events']:
            event_out = Event()
            tags = [tag.lower() for tag in event.get("tags", "").split(",")]
            event_out.start = extract_date_json(event['time'])
            event_out.end = extract_date_json(
                event.get('end_time', event['time']))
            event_out.major = "major" in tags
            if "compo" in tags:
                event_out.class_ = "Compo"
            else:
                event_out.class_ = "Event"
            event_out.url = event.get('link') or ""
            event_out.title = event.get('name' + postfix, event.get("name"))
            location = locations[language].get(location_id)
            if location is not None:
                event_out.location = location['name']
                event_out.location_url = location.get('link') or ""

            description = event.get('description' + postfix,
                                    event.get('description')) or ""
            event_out.description = description
            event_out.assemblytv_broadcast = 'tv' in tags
            events[language][event['id']] = event_out

    result = {
        'type': 'events',
        'finnish': events['fi'],
        'english': events['en'],
        'public_json': data
        }

    return result


def parse_locations(context, data):
    fields = ('location_id',
              'location_en',
              'location_fi',
              'location_url',
              'description_en',
              'description_fi')
    reader = get_csv_reader(data, "location_id;location_en", fields)

    # Ignore the first row
    reader.next()

    finnish = {}
    english = {}

    for row in reader:
        for locations, lang in [(finnish, 'fi'), (english, 'en')]:
            location = Location()
            location.name = row['location_%s' % lang].decode("utf-8")
            location.url = row['location_url']
            location.description = row['description_%s' % lang].decode("utf-8")
            locations[row['location_id']] = location

    result = {
        'type': 'locations',
        'finnish': finnish,
        'english': english
        }

    return result


def update_schedule(view, data):
    if data is None:
        view.flash('Saved changes.')
        return

    if data == "":
        view.flash(u"Empty data file was given!.", "warning")
        return

    parsers = [parse_json, parse_csv, parse_locations, parse_newcsv]
    result = None
    for parser in parsers:
        try:
            result = parser(view.context, data)
        except InvalidParserError, e:
            continue
        except ScheduleImportError, e:
            for flash_params in e.messages:
                view.flash(*flash_params)
            return

    if not result:
        view.flash(u"No appropriate parser found for the data.", "warning")
        return

    page = view.context.page

    finnish = view.context.parameters.replace('lang:*', 'lang:fi')
    finnish = page.getEdition(finnish, create=True)
    # XXX generations for this kind of data.
    if not finnish.locations:
        finnish.locations = BTrees.OOBTree.OOBTree()

    english = view.context.parameters.replace('lang:*', 'lang:en')
    english = page.getEdition(english, create=True)
    # XXX generations for this kind of data.
    if not english.locations:
        english.locations = BTrees.OOBTree.OOBTree()

    if result['type'] == "events":
        rows = update_schedule_events(finnish, result['finnish'], result)
        rows = update_schedule_events(english, result['english'], result)
        view.flash(u'Your schedule was imported successfully with %d events.' %
                   rows)

    if result['type'] == "locations":
        rows = update_schedule_locations(finnish, result['finnish'])
        rows = update_schedule_locations(english, result['english'])
        view.flash(
            u'Your schedule was imported successfully with %d locations.' %
            rows)

    public_writer = CsvWriter()
    for event_id in finnish.events.keys():
        event_en = english.events[event_id]
        event_fi = finnish.events[event_id]
        public_writer(event_id, event_en, event_fi)

    public_csv = public_writer.getCsv()

    finnish.public_csv = public_csv
    english.public_csv = public_csv

    zope.event.notify(grok.ObjectModifiedEvent(finnish))
    zope.event.notify(grok.ObjectModifiedEvent(english))


def update_schedule_events(schedule, events, result):
    schedule.events.clear()

    locations = schedule.locations

    if 'public_json' in result:
        schedule.public_json = result['public_json']
    for event_id, event in events.items():
        schedule.events[event_id] = event
        location_id = event.location_id
        if location_id in locations:
            location = locations[location_id]
            event.location = location.name
            event.location_url = location.url

    rows = len(events)
    return rows


def update_schedule_locations(schedule, locations):
    schedule.locations.clear()
    for location_id, location in locations.items():
        schedule.locations[location_id] = location

    for event_id, event in schedule.events.items():
        if event.location_id in locations:
            location = locations[event.location_id]
            event.location = location.name
            event.location_url = location.url

    return len(locations)


class Edit(asm.cmsui.form.EditForm):
    form_fields = grok.AutoFields(asm.schedule.interfaces.IScheduleUpload)
    form_fields['message'].custom_widget = asm.cmsui.tinymce.TinyMCEWidget

    @grok.action(u'Upload')
    def upload(self, data=None, title=None, message=None):
        self.context.title = title
        self.context.message = message
        zope.event.notify(grok.ObjectModifiedEvent(self.context))

        update_schedule(self, data)


class UploadSchedule(grok.Form):
    grok.context(Schedule)
    form_fields = grok.Fields(data=zope.schema.Text(title=u'Data'))

    def flash(self, message, level=''):
        self.messages.append(message)

    @grok.action(u'Upload')
    def upload(self, data=None):
        if data is None:
            return "Give data"
        self.messages = []
        update_schedule(self, data.encode("utf-8"))
        if len(self.messages):
            return "\n".join(self.messages)
        return "OK"


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


def extract_date_newcsv(date):
    return datetime.datetime.strptime(date, "%d.%m.%y %H:%M")


def extract_date_oldcsv(date):
    return datetime.datetime.strptime(date, "%a %d.%m.%y %H:%M")


def extract_date_json(date):
    return datetime.datetime.strptime(date[:len("yyyy-mm-ddThh:mm:ss")],
                                      "%Y-%m-%dT%H:%M:%S")


def format_date(date_object):
    return date_object.strftime("%a %d.%m.%y %H:%M")


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
                massaged['end_day'] = (_(event.end.strftime('%A') + '(until)')
                                       if event.start.day != event.end.day
                                       else u'')
                massaged['canceled'] = event.canceled
                massaged['assemblytv_broadcast'] = event.assemblytv_broadcast
                massaged['major'] = event.major
                hours.setdefault(event.start, []).append(massaged)

            data['hours'] = [dict(hour=i18n_strftime('%H:%M', k, self.request),
                                  events=v) for k, v in
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


class Json(grok.View):
    grok.name('json')
    grok.context(Schedule)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)

    def render(self):
        return self.context.public_json
