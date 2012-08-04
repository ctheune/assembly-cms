import unittest
import asm.schedule.schedule


class ScheduleSearchTests(unittest.TestCase):

    def test_index_empty_schedule(self):
        schedule = asm.schedule.schedule.Schedule()
        index = asm.schedule.schedule.TextIndexing(schedule)
        self.assertEqual('', index.body)

    def test_index_normal(self):
        schedule = asm.schedule.schedule.Schedule()
        schedule.title = u'Test title'
        schedule.message = u'Test message'
        event = asm.schedule.schedule.Event()
        event.title = u'Test event title'
        event.location = u'Test location'
        schedule.events[0] = event
        index = asm.schedule.schedule.TextIndexing(schedule)
        self.assertEqual(
            'Test title Test message Test event title Test location',
            index.body)

    def test_index_missing_event(self):
        schedule = asm.schedule.schedule.Schedule()
        schedule.title = u'Test title'
        schedule.message = u'Test message'
        index = asm.schedule.schedule.TextIndexing(schedule)
        self.assertEqual('Test title Test message', index.body)
