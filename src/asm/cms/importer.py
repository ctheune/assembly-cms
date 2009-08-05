# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

# XXX This module has knowledge about the assembly site. it shouldn't. I also
# think as this has knowledge about workflow, it should become its own
# extension.

import asm.cms
import asm.cms.cms
import asm.workflow
import base64
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
        export = lxml.etree.fromstring(data)
        self.base_path = export.get('base')
        for node in export:
            page = self.get_page(node.get('path'), node.tag)
            getattr(self, 'import_%s' % node.tag)(page, node)

    def import_htmlpage(self, page, node):
        content = node.text
        content = fix_relative_links(
            content, self.base_path+'/'+node.get('path'))
        edition = page.editions.next()
        edition.content = content
        asm.workflow.publish(edition)

    def import_asset(self, page, node):
        edition = page.editions.next()
        edition.content = base64.decodestring(node.text)
        asm.workflow.publish(edition)

    def get_page(self, path, type_):
        path = path.split('/')
        current = self.context
        while path:
            name = path.pop(0)
            if name not in current:
                page = asm.cms.page.Page()
                page.type = type_
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
