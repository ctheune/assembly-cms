# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import unittest
from zope.app.testing.functional import FunctionalDocFileSuite
import asm.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    t = FunctionalDocFileSuite('cms.txt', package='asm.cms')
    t.layer = asm.cms.testing.TestLayer
    suite.addTest(t)
    t = FunctionalDocFileSuite('linkbrowser.txt', package='asm.cms')
    t.layer = asm.cms.testing.TestLayer
    suite.addTest(t)
    return suite
