# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.mediagallery.interfaces
import urllib

MEDIA_WIDTH = 560.0

def get_media_info(media_id_data, default_text):
    media_id = media_id_data
    link_text = default_text
    if "|" in media_id_data:
        media_id, link_text = media_id_data.split(u"|")
    return media_id, link_text


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

    EMBED_TEMPLATE = """<object width="%(width)d" height="%(height)d"><param name="movie" value="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)d" height="%(height)d"></embed></object>"""
    CONTROLS_HEIGHT = 25.0
    ASPECT_RATIO = 16.0 / 9.0

    def link_code(self, media_id):
        return ('<a href="http://www.youtube.com/watch?v=%s">'
                'YouTube</a>') % media_id.strip()

    def embed_code(self, media_id):
        youtube_height = MEDIA_WIDTH / self.ASPECT_RATIO + self.CONTROLS_HEIGHT
        return self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'width': MEDIA_WIDTH,
            'height': youtube_height
            }


class PouetNet(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('pouet')

    def link_code(self, media_id):
        return '<a href="http://www.pouet.net/prod.php?which=%s">pouet.net</a>' % media_id.strip()


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

    EMBED_TEMPLATE = """<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%(id)s" width="%(width)d" height="%(height)d" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />"""
    CONTROLS_HEIGHT = 20.0
    ASPECT_RATIO = 16.0 / 9.0

    def link_code(self, media_id):
        link, _ = media_id.split(',')
        return ('<a href="http://demoscene.tv/prod.php?id_prod=%s">'
                'DTV</a>') % link.strip()

    def embed_code(self, media_id):
        _ , embed = media_id.split(',')
        dtv_height = MEDIA_WIDTH / self.ASPECT_RATIO + self.CONTROLS_HEIGHT
        return  self.EMBED_TEMPLATE % {
            'id': embed.strip(),
            'width': MEDIA_WIDTH,
            'height': dtv_height}


class Vimeo(grok.GlobalUtility):
    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('vimeo')

    EMBED_TEMPLATE = """<object width="%(width)d" height="%(height)d"><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id=%(id)s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=abebff&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" /><embed src="http://vimeo.com/moogaloop.swf?clip_id=%(id)s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=abebff&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="%(width)d" height="%(height)d"></embed></object>"""
    CONTROLS_HEIGHT = 0.0

    DEFAULT_ASPECT_RATIO = 16.0 / 9.0

    def _get_aspect_ratio(self, aspect_str):
        width, height = aspect_str.strip().split(":")
        return float(width)/float(height)

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

    def embed_code(self, media_id_data):
        media_id, aspect_ratio = self._get_media_data(media_id_data)
        player_height = MEDIA_WIDTH / aspect_ratio + self.CONTROLS_HEIGHT
        return  self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'width': MEDIA_WIDTH,
            'height': player_height}


class Image(grok.GlobalUtility):
    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('image')

    EMBED_TEMPLATE = """<img src='%(id)s' alt='%(image_text)s' />"""
    DEFAULT_TEXT = "Gallery image."

    def link_code(self, media_id):
        return None

    def embed_code(self, media_id_data):
        media_id, image_text = get_media_info(media_id_data, self.DEFAULT_TEXT)
        return  self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'image_text': image_text.strip()}
