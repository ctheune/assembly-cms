# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.mediagallery.interfaces
import urllib

MEDIA_WIDTH = 560.0


class DownloadURLService(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('download')

    def link_code(self, id):
        return '<a href="%s">Download</a>' % id


class YoutubeHosted(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('youtube')

    def link_code(self, id):
        return ('<a href="http://www.youtube.com/watch?v=%s">'
                'YouTube</a>') % id

    def embed_code(self, id):
        youtube_player_controls_height = 15.0
        youtube_height = MEDIA_WIDTH * 9.0 / 16.0 + youtube_player_controls_height
        return """<object width="%(width)d" height="%(height)d"><param name="movie" value="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%(id)s&amp;hl=en_US&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)d" height="%(height)d"></embed></object>""" % {
            'id': id,
            'width': MEDIA_WIDTH,
            'height': youtube_height
            }


class PouetNet(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('pouet')

    def link_code(self, id):
        return '<a href="http://www.pouet.net/prod.php?which=%s">pouet.net</a>' % id


class SceneOrgDownload(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IContentHostingService)
    grok.name('sceneorg')

    def link_code(self, id):
        return ('<a href="http://www.scene.org/file.php?file=%s">scene.org</a>' %
                urllib.quote_plus(id))


class DemoSceneTV(grok.GlobalUtility):

    grok.provides(asm.mediagallery.interfaces.IEmbeddableContentHostingService)
    grok.name('demoscenetv')

    def link_code(self, id):
        link, _ = id.split(',')
        return ('<a href="http://demoscene.tv/prod.php?id_prod=%s">'
                'DTV</a>') % link

    def embed_code(self, id):
        _ , embed = id.split(',')
        dtv_player_controls_height = 20.0
        dtv_height = MEDIA_WIDTH * 3.0 / 4.0 + dtv_player_controls_height
        return  """<embed src="http://www.demoscene.tv/mediaplayer.swf?id=%(id)s" width="%(width)d" height="%(height)d" allowfullscreen="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />""" % {
            'id': embed,
            'width': MEDIA_WIDTH,
            'height': dtv_height}


class Vimeo(object):
    pass
