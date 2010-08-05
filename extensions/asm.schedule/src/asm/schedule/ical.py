# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.schedule.schedule
import icalendar
import datetime


class ICal(grok.View):

    grok.context(asm.schedule.schedule.Schedule)
    grok.name('schedule.ics')

    def render(self):
        cal = icalendar.Calendar()
        cal.add('prodid', '-//asm.cms//Assembly Organizing//')
        stamp = datetime.datetime.now()

        for event in self.context.events.values():
            ievent = icalendar.Event()
            ievent.add('summary', event.title)
            ievent.add('location', event.location)
            ievent.add('categories', event.class_)
            ievent.add('dtstart', event.start)
            ievent.add('url', event.url)
            ievent.add('dtend', event.end)
            ievent.add('dtstamp', stamp)
            cal.add_component(ievent)

        self.request.response.setHeader('Content-Type', 'text/calendar')
        return cal.as_string()
