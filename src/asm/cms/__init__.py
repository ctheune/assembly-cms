import grok
import lxml.etree


def application(self):
    obj = self.context
    while obj is not None:
        if isinstance(obj, grok.Application):
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")

grok.View.application = property(fget=application)


def resolve_relative_urls(self, content, source):
    # Hrgh. Why is there no obvious simple way to do this?
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainerwrappercafebabe>%s</stupidcontainerwrappercafebabe>' %
        content)
    document = lxml.etree.fromstring(document, parser)
    base = self.url(source)
    for a in document.xpath('//a'):
        href = a.get('href')
        if href and not (href.startswith('http:') or
                         href.startswith('/') or
                         href.startswith('#') or
                         href.startswith('?')):
            a.set('href', base + '/' + href)
    for img in document.xpath('//img'):
        src = img.get('src')
        if src and not (src.startswith('http:') or
                        src.startswith('/') or
                        src.startswith('#') or
                        src.startswith('?')):
            img.set('src', base + '/' + src)

    result = lxml.etree.tostring(
        document.xpath('//stupidcontainerwrappercafebabe')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainerwrappercafebabe>', '')
    result = result.replace('</stupidcontainerwrappercafebabe>', '')
    return result.strip()


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
