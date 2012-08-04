import asm.cmsui.format
import datetime
import unittest


class FormatTests(unittest.TestCase):

    def test_datetime(self):
        format = asm.cmsui.format.DateFormat(
            datetime.datetime(2009, 10, 9, 16, 12), None)
        self.assertEquals('09.10.2009 16:12', format.render())
