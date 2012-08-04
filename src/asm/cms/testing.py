import asm.cms.cms
import os.path
import transaction
import zope.app.component.hooks
import zope.app.testing.functional


TestLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=False)


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):

    layer = TestLayer

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        r = self.getRootFolder()
        r['cms'] = self.cms = asm.cms.cms.CMS()
        zope.app.component.hooks.setSite(self.cms)
        transaction.commit()

    def tearDown(self):
        zope.app.component.hooks.setSite(None)
        super(FunctionalTestCase, self).tearDown()
