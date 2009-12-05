# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import os.path
import zope.app.testing.functional
import gocept.selenium.ztk


TestLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=False)


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):

    layer = TestLayer


class SeleniumTestCase(gocept.selenium.ztk.TestCase):

    layer = gocept.selenium.ztk.Layer(TestLayer)
