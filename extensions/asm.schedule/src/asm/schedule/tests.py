# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
from zope.app.testing.functional import FunctionalDocFileSuite
import asm.cms.edition
import asm.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    t = FunctionalDocFileSuite('schedule.txt', package='asm.schedule')
    t.layer = asm.cms.testing.TestLayer
    suite.addTest(t)
    return suite
