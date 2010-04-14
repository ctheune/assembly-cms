# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.testing
import zope.testbrowser.testing


class PreviewTests(asm.cms.testing.FunctionalTestCase):

    def test_preview_not_broken(self):
        # Very simple smoke test to ensure that the preview template actually
        # renders. I've seen this break when renaming static resources.
        b = zope.testbrowser.testing.Browser()
        b.open('http://localhost/cms/@@preview-window')
