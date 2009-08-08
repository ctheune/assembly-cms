# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.cms
import asm.cms.edition
import base64
import bn
import datetime
import grok
import lxml.etree
import os.path
import pytz
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
        for page_node in export:
            page = self.get_page(page_node.get('path'), page_node.tag)

            for edition_node in page_node:
                assert edition_node.tag == 'edition'
                parameters = set(edition_node.get('parameters').split())
                parameters = asm.cms.edition.EditionParameters(parameters)
                edition = page.getEdition(parameters, create=True)
                getattr(self, 'import_%s' % page.type)(edition, edition_node)
                edition.title = edition_node.get('title')
                edition.tags = edition_node.get('tags')
                edition.modified = extract_date(edition_node.get('modified'))
                edition.created = extract_date(edition_node.get('created'))
                zope.event.notify(grok.ObjectModifiedEvent(edition))

    def import_htmlpage(self, edition, node):
        content = base64.decodestring(node.text)
        content = fix_relative_links(
            content, self.base_path+'/'+node.getparent().get('path'))
        edition.content = content

    def import_asset(self, edition, node):
        edition.content = base64.decodestring(node.text)

    def get_page(self, path, type_):
        path = path.split('/')
        current = self.context
        if path == ['']:
            # Ugly hack to support importing content on the root page.
            return current
        while path:
            name = path.pop(0)
            if name not in current:
                page = asm.cms.page.Page()
                page.type = type_
                current[name] = page
                # We're importing: remove any initial variations and only use
                # content from import.
                for edition in page.editions:
                    del page[edition.__name__]
            current = current.get(name)
        return current


def fix_relative_links(document, current_path):
    # XXX Hrgh. Why is there no obvious simple way to do this?
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainerwrappercafebabe>%s</stupidcontainerwrappercafebabe>' %
        document.decode('utf-8'))
    document = lxml.etree.fromstring(document, parser)
    for a in document.xpath('//a'):
        href = a.get('href')
        if href and href.startswith('/'):
            a.set('href', bn.relpath(href, current_path))
    for img in document.xpath('//img'):
        src = img.get('src')
        if src and src.startswith('/'):
            img.set('src', bn.relpath(src, current_path))

    result = lxml.etree.tostring(document.xpath('//stupidcontainerwrappercafebabe')[0],
                                 pretty_print=True)
    result = result.replace('<stupidcontainerwrappercafebabe>', '')
    result = result.replace('</stupidcontainerwrappercafebabe>', '')
    return result.strip()


def extract_date(str):
    if not str:
        return datetime.datetime.now(pytz.UTC)
    date = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return date.replace(tzinfo=pytz.UTC)
