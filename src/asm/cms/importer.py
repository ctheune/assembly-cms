# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

# XXX This module has knowledge about the assembly site. it shouldn't. I also
# think as this has knowledge about workflow, it should become its own
# extension.

import asm.cms
import asm.cms.cms
import asm.workflow
import bn
import grok
import lxml.etree
import os.path
import zope.interface
import zope.schema
import zope.traversing.api


class ImportActions(grok.Viewlet):

    grok.viewletmanager(asm.cms.cmsui.Actions)
    grok.context(asm.cms.cms.CMS)


class IImport(zope.interface.Interface):

    data = zope.schema.Bytes(title=u'Content')


class Import(asm.cms.Form):

    grok.context(asm.cms.cms.CMS)
    form_fields = grok.AutoFields(IImport)

    @grok.action(u'Import')
    def do_import(self, data):
        etree = lxml.etree.fromstring(data)
        for page in etree.iterfind('page'):
            page_ob = self.get_page(page.get('path'))
            content = page.text
            # XXX the base path of the original site should be written in the
            # original output instead of knowing the structure in here ...
            content = fix_relative_links(
                content, zope.traversing.api.getPath(page_ob))
            edition = page_ob.editions.next()
            edition.content = content
            asm.workflow.publish(edition)

    def get_page(self, path):
        path = path.split('/')
        current = self.context
        while path:
            name = path.pop(0)
            if name not in current:
                page = asm.cms.page.Page()
                page.type = 'htmlpage'
                current[name] = page
            current = current.get(name)
        return current

def fix_relative_links(document, current_path):
    # XXX Hrgh. Why is there no obvious simple way to do this?
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainerwrappercafebabe>%s</stupidcontainerwrappercafebabe>' %
        document)
    document = lxml.etree.fromstring(document, parser)
    for a in document.xpath('//a'):
        href = a.get('href')
        if href and href.startswith('/'):
            a.set('href', bn.relpath(href, current_path))
    for img in document.xpath('//img'):
        src = img.get('src')
        if src and src.startswith('/'):
            img.set('src', bn.relpath(src, current_path))

    result = lxml.etree.tostring(document, pretty_print=True)
    result = result.replace('<stupidcontainerwrappercafebabe>', '')
    result = result.replace('</stupidcontainerwrappercafebabe>', '')
    return result.strip()
