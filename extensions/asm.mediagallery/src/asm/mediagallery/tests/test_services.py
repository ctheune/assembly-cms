import asm.cms.testutils
import asm.mediagallery.services

class ServiceTests(asm.cms.testutils.TestCase):

    def test_download_url_link_code_is_ok(self):
        service = asm.mediagallery.services.DownloadURLService()
        code = service.link_code('link')
        self.assertValidXml(code)
        self.assertIn('link', code)

    def test_download_url_link_text_is_ok(self):
        service = asm.mediagallery.services.DownloadURLService()
        code = service.link_code('link|link text')
        self.assertValidXml(code)
        self.assertIn('link text', code)

    def test_youtube_link_code_is_ok(self):
        service = asm.mediagallery.services.YoutubeHosted()
        code = service.link_code('youtube-id')
        self.assertValidXml(code)
        self.assertIn('youtube-id', code)

    def test_youtube_embed_code_is_ok(self):
        service = asm.mediagallery.services.YoutubeHosted()
        code = service.embed_code('youtube-id')
        self.assertValidXml(code)
        self.assertIn('youtube-id', code)

    def test_pouet_link_code_is_valid_xml(self):
        service = asm.mediagallery.services.PouetNet()
        link_code = service.link_code('pouet-id')
        self.assertValidXml(link_code)
        self.assertIn('pouet-id', link_code)

    def test_scene_org_link_code_is_ok(self):
        service = asm.mediagallery.services.SceneOrgDownload()
        code = service.link_code('/link/path')
        self.assertValidXml(code)

        named_code = service.link_code('/link/path|link text')
        self.assertValidXml(named_code)
        self.assertIn('link text', named_code)

    def test_demoscene_tv_link_code_is_ok(self):
        service = asm.mediagallery.services.DemosceneTV()
        code = service.link_code('link-id,embed-id')
        self.assertValidXml(code)
        self.assertIn('link-id', code)

    def test_demoscene_tv_embed_code_is_ok(self):
        service = asm.mediagallery.services.DemosceneTV()
        code = service.embed_code('link-id,embed-id')
        self.assertValidXml(code)
        self.assertIn('embed-id', code)

    def test_vimeo_link_code_is_ok(self):
        service = asm.mediagallery.services.Vimeo()
        code = service.link_code('vimeo-id')
        self.assertValidXml(code)
        self.assertIn('vimeo-id', code)

        aspected_code = service.link_code('vimeo-id,4:3')
        self.assertValidXml(aspected_code)
        self.assertIn('vimeo-id', aspected_code)

    def test_vimeo_embed_code_is_ok(self):
        service = asm.mediagallery.services.Vimeo()
        code = service.embed_code('vimeo-id')
        self.assertValidXml(code)
        self.assertIn('vimeo-id', code)

        aspected_code = service.embed_code('vimeo-id,4:3')
        self.assertValidXml(aspected_code)
        self.assertIn('vimeo-id', aspected_code)

    def test_vimeo_link_code_is_none(self):
        service = asm.mediagallery.services.Image()
        self.assertIsNone(service.link_code('image-id'))

    def test_vimeo_embed_code_is_ok(self):
        service = asm.mediagallery.services.Image()
        code = service.embed_code('image-id')
        self.assertValidXml(code)
        self.assertIn('image-id', code)

        described_code = service.embed_code('image-id|Image text')
        self.assertValidXml(described_code)
        self.assertIn('image-id', described_code)
        self.assertIn('Image text', described_code)
