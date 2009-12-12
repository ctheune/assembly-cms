import asm.cms.utils
import grok


def application(self):
    obj = self.context
    while obj is not None:
        if isinstance(obj, grok.Application):
            self.__dict__['application'] = obj
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")


def application_url(self):
    url = old_application_url(self)
    self.application_url = lambda: url
    return url


old_application_url = grok.View.application_url
grok.View.application_url = application_url
grok.View.application = property(fget=application)


def resolve_relative_urls(self, content, source):
    base = self.url(source)

    def resolve(url):
        for prefix in ['http:', 'ftp:', 'https:', 'mailto:', 'irc:', '/', '?',
                       '#']:
            if url.startswith(prefix):
                return
        return base + '/' + url

    return asm.cms.utils.rewrite_urls(content, resolve)

grok.View.resolve_relative_urls = resolve_relative_urls

# Provide re-exports of public API

import zope.deferredimport

zope.deferredimport.define(
    Edition='asm.cms.edition:Edition',

    Actions='asm.cms.cmsui:Actions',
    ActionView='asm.cms.cmsui:ActionView',
    Notes='asm.cms.cmsui:Notes',

    Form='asm.cms.form:Form',
    EditForm='asm.cms.form:EditForm',
    AddForm='asm.cms.form:AddForm',

    Pagelet='asm.cms.retail:Pagelet',

    IRetailSkin='asm.cms.interfaces:IRetailSkin',
    ICMSSkin='asm.cms.interfaces:ICMSSkin',
    IPage='asm.cms.interfaces:IPage',
    IEditionFactory='asm.cms.interfaces:IEditionFactory',
    IEdition='asm.cms.interfaces:IEdition',
    IEditionSelector='asm.cms.interfaces:IEditionSelector',
    IInitialEditionParameters='asm.cms.interfaces:IInitialEditionParameters',
    )
