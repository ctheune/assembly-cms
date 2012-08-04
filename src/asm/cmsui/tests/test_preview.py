import asm.cmsui.testing


class PreviewTests(asm.cmsui.testing.SeleniumTestCase):

    def test_preview_not_broken(self):
        # Very simple smoke test to ensure that the preview template actually
        # renders. I've seen this break when renaming static resources.
        self.selenium.open(
            'http://mgr:mgrpw@%s/++skin++cms/cms/@@preview-window' %
            self.selenium.server)
