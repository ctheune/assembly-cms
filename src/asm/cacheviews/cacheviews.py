import asm.cms.utils
import datetime
import grok
import zope.component
import zope.interface


class Cache(grok.View):
    grok.context(zope.interface.Interface)

    default_cache_time = datetime.timedelta(weeks=2)

    def update(self, cache_seconds=None):
        utcnow = datetime.datetime(2009, 1, 1).utcnow()
        cache_time = self.default_cache_time
        if cache_seconds is not None:
            seconds = int(cache_seconds)
            if seconds >= 0:
                cache_time = datetime.timedelta(seconds=seconds)

        expiresAt = utcnow + cache_time

        self.request.response.setHeader(
            "Expires",
            asm.cms.utils.datetime_to_http_timestamp(expiresAt)
            )
        max_age = cache_time.seconds + cache_time.days * 86400
        self.request.response.setHeader(
            "Cache-Control",
            "max-age=%d,public" % max_age)
        self.request.response.setHeader(
            'Vary', 'Accept-Encoding,Accept-Language,Cookie,Authorization')

    def render(self):
        # XXX this should work for any view and not just assume index view.
        # For example static resources do not work with this.
        return zope.component.getMultiAdapter(
            (self.context, self.request), zope.interface.Interface,
            name='index')()
