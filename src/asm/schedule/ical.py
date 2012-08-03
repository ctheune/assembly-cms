# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.schedule.schedule
import datetime
import grok
import icalendar
import re


class ScheduleWrapper(object):

    def __init__(self, content_type, events):
        self.content_type = content_type
        self.events = events


class CalendarView(grok.View):
    grok.context(ScheduleWrapper)
    grok.name("index.html")

    def render(self):
        cal = icalendar.Calendar()
        cal.add('prodid', '-//asm.cms//Assembly Organizing//')
        stamp = datetime.datetime.now()

        for event in self.context.events:
            ievent = icalendar.Event()
            ievent.add('summary', event.title)
            ievent.add('location', event.location)
            ievent.add('categories', event.class_)
            ievent.add('dtstart', event.start)
            url = event.url
            # A hack to make imported URL data to have the site address correct.
            if re.match("/[^/]", url):
                url = "http://www.assembly.org%s" % url

            ievent.add('url', url)
            ievent.add('dtend', event.end)
            ievent.add('dtstamp', stamp)
            cal.add_component(ievent)

        self.request.response.setHeader('Content-Type', self.context.content_type)

        return cal.as_string()


class IcalendarScheduleTraverser(grok.Traverser):
    grok.context(asm.schedule.schedule.Schedule)

    EVENTNAME_PREFIX = "event-"

    def traverse(self, name):
        if name.endswith('.vcs'):
            content_type = "text/x-vCalendar"
            suffix = '.vcs'
        elif name.endswith('.ics'):
            content_type = "text/calendar"
            suffix = '.ics'
        else:
            return None

        if name.startswith(self.EVENTNAME_PREFIX):
            event_id_str = name.lstrip(self.EVENTNAME_PREFIX)
            event_id_str = event_id_str.rstrip(suffix)
            try:
                event_id = int(event_id_str)
            except:
                return None
            if event_id not in self.context.events:
                return None
            events = [self.context.events[event_id]]
        else:
            events = self.context.events.values()

        return ScheduleWrapper(content_type, events)
