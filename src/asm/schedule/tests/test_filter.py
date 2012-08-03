# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.edition
import asm.schedule.schedule


class ScheduleFilterTests(unittest.TestCase):

    def test_filter_all_days_all_categories(self):
        schedule = asm.schedule.schedule.Schedule()
