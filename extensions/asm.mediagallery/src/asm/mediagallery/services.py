# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.mediagallery.interfaces
import urllib

MEDIA_WIDTH = 560.0


class DownloadURLService(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('download')

    def link_code(self, media_id):
        return '<a href="%s">Download</a>' % media_id.strip()


class YoutubeHosted(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('youtube')

    EMBED_TEMPLATE = """<object width="%(width)d" height="%(height)d"><param name="movie" value="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)d" height="%(height)d"></embed></object>"""
    CONTROLS_HEIGHT = 25.0

    def link_code(self, media_id):
        return ('<a href="http://www.youtube.com/watch?v=%s">'
                'YouTube</a>') % media_id.strip()

    def embed_code(self, media_id):
        youtube_height = MEDIA_WIDTH * 9.0 / 16.0 + self.CONTROLS_HEIGHT
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

    def link_code(self, media_id):
        return ('<a href="http://www.scene.org/file.php?file=%s">scene.org</a>' %
                urllib.quote_plus(media_id.strip()))


class DemosceneTV(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('demoscenetv')

    EMBED_TEMPLATE = """<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%(id)s" width="%(width)d" height="%(height)d" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />"""
    CONTROLS_HEIGHT = 20.0

    def link_code(self, media_id):
        link, _ = media_id.split(',')
        return ('<a href="http://demoscene.tv/prod.php?id_prod=%s">'
                'DTV</a>') % link.strip()

    def embed_code(self, media_id):
        _ , embed = media_id.split(',')
        dtv_height = MEDIA_WIDTH * 3.0 / 4.0 + self.CONTROLS_HEIGHT
        return  self.EMBED_TEMPLATE % {
            'id': embed.strip(),
            'width': MEDIA_WIDTH,
            'height': dtv_height}


class Vimeo(object):
    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('vimeo')

    EMBED_TEMPLATE = """<object width="%(width)d" height="%(height)d"><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id=%(id)s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=abebff&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" /><embed src="http://vimeo.com/moogaloop.swf?clip_id=%(id)s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=abebff&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="%(width)d" height="%(height)d"></embed></object>"""
    CONTROLS_HEIGHT = 0.0

    def link_code(self, media_id):
        return "<a href='http://vimeo.com/%s'>Vimeo</a>" % media_id.strip()

    def embed_code(self, media_id):
        player_height = MEDIA_WIDTH * 9.0 / 16.0 + self.CONTROLS_HEIGHT
        return  self.EMBED_TEMPLATE % {
            'id': media_id.strip(),
            'width': MEDIA_WIDTH,
            'height': player_height}
