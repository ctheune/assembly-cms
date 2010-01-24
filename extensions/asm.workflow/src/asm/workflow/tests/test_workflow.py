# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import os.path
import zope.app.testing.functional
import asm.cms.edition
import asm.cms.testing
import gocept.selenium.ztk


TestLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=False)


class SeleniumTestCase(asm.cms.testing.SeleniumTestCase):

    layer = gocept.selenium.ztk.Layer(TestLayer)

    def testWorkflow(self):
        s = self.selenium
        s.click('css=#version h3')
        s.clickAndWait('css=#publish')
        s.assertTextPresent('Published draft')
