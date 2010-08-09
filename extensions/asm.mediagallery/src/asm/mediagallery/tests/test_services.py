import asm.cms.testutils
import asm.mediagallery.services

class ServiceTests(asm.cms.testutils.TestCase):

    def test_download_url_link_code_is_ok(self):
        service = asm.mediagallery.services.DownloadURLService()
        code = service.link_code('link')
        self.assertValidXml(code)
        self.assertIsIn('link', code)

    def test_youtube_link_code_is_ok(self):
        service = asm.mediagallery.services.YoutubeHosted()
        code = service.link_code('youtube-id')
        self.assertValidXml(code)
        self.assertIsIn('youtube-id', code)

    def test_youtube_embed_code_is_ok(self):
        service = asm.mediagallery.services.YoutubeHosted()
        code = service.embed_code('youtube-id')
        self.assertValidXml(code)
        self.assertIsIn('youtube-id', code)

    def test_pouet_link_code_is_valid_xml(self):
        service = asm.mediagallery.services.PouetNet()
        link_code = service.link_code('pouet-id')
        self.assertValidXml(link_code)
        self.assertIsIn('pouet-id', link_code)

    def test_scene_org_link_code_is_ok(self):
        service = asm.mediagallery.services.SceneOrgDownload()
        code = service.link_code('/link/path')
        self.assertValidXml(code)

    def test_demoscene_tv_link_code_is_ok(self):
        service = asm.mediagallery.services.DemosceneTV()
        code = service.link_code('link-id,embed-id')
        self.assertValidXml(code)
        self.assertIsIn('link-id', code)

    def test_demoscene_tv_embed_code_is_ok(self):
        service = asm.mediagallery.services.DemosceneTV()
        code = service.embed_code('link-id,embed-id')
        self.assertValidXml(code)
        self.assertIsIn('embed-id', code)

    def test_vimeo_link_code_is_ok(self):
        service = asm.mediagallery.services.Vimeo()
        code = service.link_code('vimeo-id')
        self.assertValidXml(code)
        self.assertIsIn('vimeo-id', code)

        aspected_code = service.link_code('vimeo-id,4:3')
        self.assertValidXml(aspected_code)
        self.assertIsIn('vimeo-id', aspected_code)

    def test_vimeo_embed_code_is_ok(self):
        service = asm.mediagallery.services.Vimeo()
        code = service.embed_code('vimeo-id')
        self.assertValidXml(code)
        self.assertIsIn('vimeo-id', code)

        aspected_code = service.embed_code('vimeo-id,4:3')
        self.assertValidXml(aspected_code)
        self.assertIsIn('vimeo-id', aspected_code)
