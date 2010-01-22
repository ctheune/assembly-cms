# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.testing
import unittest


class CMSUI(asm.cms.testing.SeleniumTestCase):

    def test_cms_redirects_to_editor(self):
        s = self.selenium
        s.open('http://mgr:mgrpw@%s/++skin++cms/cms' % s.server)
        self.assertEquals(
            u'http://localhost:8087/++skin++cms/cms/edition-/@@edit',
            s.getLocation())
