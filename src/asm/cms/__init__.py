import asm.cms.utils
import grok
import urlparse


def get_application(context):
    obj = context
    while obj is not None:
        if isinstance(obj, grok.Application):
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")

def get_application_for_view(self):
    return get_application(self.context)

grok.View.application = property(fget=get_application_for_view)


def cms_edition(self):
    return asm.cms.edition.select_edition(self.application, self.request)

grok.View.cms_edition = property(fget=cms_edition)


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

grok.View.resolve_relative_urls = resolve_relative_urls

# Provide re-exports of public API

import zope.deferredimport

zope.deferredimport.define(
    Edition='asm.cms.edition:Edition',
    IPage='asm.cms.interfaces:IPage',
    IEditionFactory='asm.cms.interfaces:IEditionFactory',
    IEdition='asm.cms.interfaces:IEdition',
    IEditionSelector='asm.cms.interfaces:IEditionSelector',
    IInitialEditionParameters='asm.cms.interfaces:IInitialEditionParameters',
    )
