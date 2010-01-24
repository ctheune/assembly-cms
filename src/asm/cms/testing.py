# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import os.path
import zope.app.testing.functional
import gocept.selenium.ztk
import asm.cms.cms
import transaction


TestLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=False)


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):

    layer = TestLayer


class SeleniumTestCase(gocept.selenium.ztk.TestCase):

    layer = gocept.selenium.ztk.Layer(TestLayer)

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        r = self.getRootFolder()
        r['cms'] = self.cms = asm.cms.cms.CMS()
        transaction.commit()
        self.selenium.open('http://mgr:mgrpw@%s/++skin++cms/cms' %
                           self.selenium.server)
