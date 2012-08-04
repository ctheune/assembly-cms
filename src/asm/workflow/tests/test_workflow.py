import asm.cms.edition
import asm.cmsui.testing
import gocept.selenium.ztk
import os.path
import transaction
import zope.app.testing.functional


TestLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=False)


class SeleniumTestCase(asm.cmsui.testing.SeleniumTestCase):

    layer = gocept.selenium.ztk.Layer(TestLayer)

    def testWorkflow(self):
        cms = self.getRootFolder()['cms']
        home = cms.editions.next()
        home.title = 'titlefoo'
        home.content = 'contentfoo'
        transaction.commit()
        s = self.selenium
        s.open('http://mgr:mgrpw@%s/++skin++cms/cms' % s.server)
        s.clickAndWait('name=form.actions.save')

        #Check that publish works
        s.click('css=#version h3')
        s.clickAndWait('css=#publish')
        s.assertTextPresent('Published draft')
        s.assertTextPresent('titlefoo')

        #Check that draft is still present
        s.click('css=#version h3')
        s.assertElementNotPresent('link=Draft')

        # Create new draft, check that publish works while viewing public
        # version
        s.clickAndWait('css=#draft')
        s.type('name=form.title', 'titlebar')
        s.clickAndWait('name=form.actions.save')
        s.click('css=#version h3')
        s.clickAndWait('link=Public')
        s.click('css=#version h3')
        s.assertElementNotPresent('css=#publish')
