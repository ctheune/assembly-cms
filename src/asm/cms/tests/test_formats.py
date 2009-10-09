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

    def test_bytes(self):
        format = asm.cms.cmsui.BytesFormat(25, None)
        self.assertEquals('25 Bytes', format.render())
        format.context = 400
        self.assertEquals('400 Bytes', format.render())

        format.context = 800
        self.assertEquals('0.8 KiB', format.render())
        format.context = 1024
        self.assertEquals('1 KiB', format.render())
        format.context = 1024
        self.assertEquals('1 KiB', format.render())
        format.context = 1025
        self.assertEquals('1 KiB', format.render())
        format.context = 1100
        self.assertEquals('1.1 KiB', format.render())
        format.context = 400 * 1024
        self.assertEquals('400 KiB', format.render())

        format.context = 800 * 1024
        self.assertEquals('0.8 MiB', format.render())
        format.context = 1024 * 1024
        self.assertEquals('1 MiB', format.render())
        format.context = 1024 * 1024
        self.assertEquals('1 MiB', format.render())
        format.context = 1024 * 1024 + 1
        self.assertEquals('1 MiB', format.render())
        format.context = 100 * 1024 + (1024**2)
        self.assertEquals('1.1 MiB', format.render())
        format.context = 400 * 1024**2
        self.assertEquals('400 MiB', format.render())

        format.context = 800 * 1024**2
        self.assertEquals('0.8 GiB', format.render())
        format.context = 1024 * 1024**2
        self.assertEquals('1 GiB', format.render())
        format.context = 1024 * 1024**2
        self.assertEquals('1 GiB', format.render())
        format.context = 1024 * 1024**2 + 1
        self.assertEquals('1 GiB', format.render())
        format.context = 100 * 1024**2 + (1024**3)
        self.assertEquals('1.1 GiB', format.render())
        format.context = 400 * 1024**3
        self.assertEquals('400 GiB', format.render())

        format.context = 800 * 1024**3
        self.assertEquals('800 GiB', format.render())


def test_suite():
    return unittest.makeSuite(FormatTests)
