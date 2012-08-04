import asm.cms.utils
import grok
import urlparse
import zope.component
import zope.publisher.http


def get_application(context):
    obj = context
    while obj is not None:
        if isinstance(obj, grok.Application):
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")


def get_application_for_view(self):
    return get_application(self.context)


def cms_edition(self):
    return asm.cms.edition.select_edition(self.application, self.request)


def view(self, name):
    return zope.component.getMultiAdapter(
        (self.context, self.request), name=name)


def resolve_relative_urls(self, content, source):

    def resolve(url):
        for prefix in ['http:', 'ftp:', 'https:', 'mailto:', 'irc:', '/', '?',
                       '#']:
            if url.startswith(prefix):
                return
        return urlparse.urljoin(base, url)

    # Always turn the source into a folder-like path element to avoid that
    # pointing to '.' will resolve in the parent's index.
    base = self.url(source) + '/'
    return asm.cms.utils.rewrite_urls(content, resolve)


# XXX Monkey patch to force requests to include the 'Accept-Encoding'
# in the Vary header.
def force_vary_header(self, name, value, *args, **kw):
    if name.lower() == 'vary' and 'accept-encoding' not in value.lower():
        value += ",Accept-Encoding"
    result = old_setHeader(self, name, value, *args, **kw)
    return result

old_setHeader = zope.publisher.http.HTTPResponse.setHeader


def apply_patches():
    grok.View.application = property(fget=get_application_for_view)
    grok.View.cms_edition = property(fget=cms_edition)
    grok.View.resolve_relative_urls = resolve_relative_urls
    grok.View.view = view
    zope.publisher.http.HTTPResponse.setHeader = force_vary_header
