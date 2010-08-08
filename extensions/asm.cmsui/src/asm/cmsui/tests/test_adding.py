# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.testing
import transaction


class Adding(asm.cms.testing.SeleniumTestCase):

    def test_add(self):
        s = self.selenium
        s.open('http://mgr:mgrpw@%s/++skin++cms/cms' % s.server)
        s.verifyNotVisible('css=#add-page')
        s.click('css=#actions .toggle-navigation')
        s.verifyVisible('css=#add-page')
        s.type('css=form[name="addpage"] input[name="title"]', 'A test')
        s.clickAndWait('css=#add-page')
        self.assertEquals(
            u'http://localhost:8087/++skin++cms/cms/a-test/edition-/@@edit',
            s.getLocation())
        transaction.begin()
        test = self.getRootFolder()['cms']['a-test']
        self.assertEquals('htmlpage', test.type)
        self.assertEquals('A test', test['edition-'].title)
