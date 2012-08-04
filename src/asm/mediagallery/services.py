import asm.mediagallery.interfaces
import cgi
import grok
import urllib
import urlparse


def get_media_info(media_id_data, default_text):
    media_id = media_id_data
    link_text = default_text
    if "|" in media_id_data:
        media_id, link_text = media_id_data.split(u"|")
    return media_id, link_text


def calculate_embed_size(aspect_ratio, controls_height, width):
    height = float(width) / aspect_ratio + controls_height
    return width, height


class DownloadURLService(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('download')
    DEFAULT_LINK_TEXT = u"Download"

    def link_code(self, media_id_data):
        link_address, link_text = get_media_info(
            media_id_data, self.DEFAULT_LINK_TEXT)
        return u'<a href="%s">%s</a>' % (link_address, link_text)


class YoutubeHosted(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('youtube')

    YOUTUBE_PARAMETERS = "&amp;hl=en_US&amp;fs=1&amp;enablejsapi=1&amp;showinfo=0&amp;modestbranding=1&amp;autoplay=1&amp;playerapiid=ytplayerembed&amp;origin=%(origin)s"  # NOQA
    EMBED_TEMPLATE = '<iframe id="ytplayerembed" class="youtube-player" width="%(width)d" height="%(height)d" src="http://www.youtube.com/embed/%(id)s?%(params)s" style="border: 0">\n</iframe>'  # NOQA
    CONTROLS_HEIGHT = 25.0
    ASPECT_RATIO = 16.0 / 9.0
    DEFAULT_WIDTH = 640

    def link_code(self, media_id):
        return ('<a href="http://www.youtube.com/watch?v=%s">'
                'YouTube</a>') % media_id.strip()

    def embed_code(self, request, media_id, max_width=DEFAULT_WIDTH,
                   max_height=None):
        width, height = calculate_embed_size(
            self.ASPECT_RATIO, self.CONTROLS_HEIGHT, max_width)
        origin = urlparse.urlparse(request.getApplicationURL()).netloc
        parameters = self.YOUTUBE_PARAMETERS % {'origin': origin}
        return self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'width': width,
            'height': height,
            'params': parameters,
            }


class PouetNet(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('pouet')

    POUET_LINK = (
        '<a href="http://www.pouet.net/prod.php?which=%s">pouet.net</a>')

    def link_code(self, media_id):
        return self.POUET_LINK % media_id.strip()


class SceneOrgDownload(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('sceneorg')

    DEFAULT_LINK_TEXT = u"scene.org"

    def link_code(self, media_id_data):
        media_id, link_text = get_media_info(
            media_id_data, self.DEFAULT_LINK_TEXT)
        return (u'<a href="http://www.scene.org/file.php?file=%s">%s</a>' %
                (urllib.quote_plus(media_id.strip()), link_text))


class DemosceneTV(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('demoscenetv')

    EMBED_TEMPLATE = """
<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%(id_file)s_%(id_prod)s_%(id_app)s" width="%(width)s" height="%(height)s" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />""" # NOQA
    CONTROLS_HEIGHT = 20.0
    ASPECT_RATIO = 16.0 / 9.0
    DEFAULT_WIDTH = 512

    def _get_vars(self, media_id):
        return dict(map(lambda x: (x[0], x[1][0]),
                        cgi.parse_qs(media_id).items()))

    def link_code(self, media_id):
        media_vars = self._get_vars(media_id)
        return ('<a href="http://demoscene.tv/prod.php?id_prod=%s">'
                'DTV</a>') % media_vars['id_prod']

    def embed_code(self, request, media_id, max_width=DEFAULT_WIDTH,
                   max_height=None):
        media_vars = self._get_vars(media_id)
        width = int(media_vars['width'])
        height = int(media_vars['height'])
        aspect = float(width) / height
        new_width, new_height = calculate_embed_size(aspect, 0, max_width)
        media_vars['width'] = new_width
        media_vars['height'] = new_height
        return self.EMBED_TEMPLATE % media_vars


class Vimeo(grok.GlobalUtility):
    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('vimeo')

    EMBED_TEMPLATE = """<iframe src="http://player.vimeo.com/video/%(id)s?autoplay=1" width="%(width)d" height="%(height)d" frameborder="0"></iframe>""" # NOQA

    CONTROLS_HEIGHT = 0.0

    DEFAULT_ASPECT_RATIO = 16.0 / 9.0
    DEFAULT_WIDTH = 400

    def _get_aspect_ratio(self, aspect_str):
        width, height = aspect_str.strip().split(":")
        return float(width) / float(height)

    def _get_media_data(self, media_id_data):
        if "," in media_id_data:
            media_id, aspect_ratio_str = media_id_data.split(",")
            aspect_ratio = self._get_aspect_ratio(aspect_ratio_str)
        else:
            media_id = media_id_data
            aspect_ratio = self.DEFAULT_ASPECT_RATIO
        return media_id, aspect_ratio

    def link_code(self, media_id_data):
        media_id, _ = self._get_media_data(media_id_data)
        return "<a href='http://vimeo.com/%s'>Vimeo</a>" % media_id.strip()

    def embed_code(self, request, media_id_data, max_width=DEFAULT_WIDTH,
                   max_height=None):
        media_id, aspect_ratio = self._get_media_data(media_id_data)

        width, height = calculate_embed_size(
            aspect_ratio, self.CONTROLS_HEIGHT, max_width)

        return self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'width': width,
            'height': height}


class Image(grok.GlobalUtility):
    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('image')

    EMBED_TEMPLATE = """<img src="%(id)s" alt="%(image_text)s" />"""
    DEFAULT_TEXT = "Gallery image."

    def link_code(self, media_id):
        return None

    def embed_code(self, request, media_id_data, max_width=None,
                   max_height=None):
        media_id, image_text = get_media_info(media_id_data, self.DEFAULT_TEXT)
        return self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'image_text': cgi.escape(image_text.strip(), quote=True)}
