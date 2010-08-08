# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import asm.cms.cmsui
import datetime


class FormatTests(unittest.TestCase):

    def test_datetime(self):
        format = asm.cms.cmsui.DateFormat(
            datetime.datetime(2009, 10, 9, 16, 12), None)
        self.assertEquals('09.10.2009 16:12', format.render())
