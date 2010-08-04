# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.cms
import asm.cms.edition
import base64
import datetime
import grok
import lxml.etree
import os.path
import pytz
import zope.exceptions.interfaces
import zope.interface
import zope.schema
import zope.traversing.api


class ImportActions(grok.Viewlet):

    grok.viewletmanager(asm.cms.NavigationToolActions)
    grok.context(zope.interface.Interface)


class IImport(zope.interface.Interface):

    data = zope.schema.Bytes(
        title=u'Content',
        description=(u'The content is expected to be in the Assembly CMS '
                     u'XML import format.'))


class Import(asm.cms.Form):

    grok.context(asm.cms.cms.CMS)
    form_fields = grok.AutoFields(IImport)

    @grok.action(u'Import')
    def import_action(self, data):
        self.do_import(data)

    def do_import(self, data):
        export = lxml.etree.fromstring(data)
        self.base_path = export.get('base')
        for page_node in export:
            page = self.get_page(page_node.get('path'), page_node.tag)

            for edition_node in page_node:
                assert edition_node.tag == 'edition'
                parameters = set(edition_node.get('parameters').split())
                parameters = asm.cms.edition.EditionParameters(parameters)
                if 'lang:' in parameters:
                    # ensure that the fallback language is english
                    parameters = parameters.replace('lang:', 'lang:en')
                try:
                    edition = page.addEdition(parameters)
                except zope.exceptions.interfaces.DuplicationError:
                    # Leave existing content alone.
                    continue
                getattr(self, 'import_%s' % page.type)(edition, edition_node)
                edition.title = edition_node.get('title')
                edition.tags = edition_node.get('tags')
                edition.modified = extract_date(edition_node.get('modified'))
                edition.created = extract_date(edition_node.get('created'))
                zope.event.notify(grok.ObjectModifiedEvent(edition))

    def import_htmlpage(self, edition, node):
        content = base64.decodestring(node.text).decode('utf-8')
        fix_relative_links(
            content, self.base_path + '/' + node.getparent().get('path'))
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
                page = asm.cms.page.Page(type_)
                current[name] = page
                # We're importing: remove any initial variations and only use
                # content from import.
                for edition in page.editions:
                    del page[edition.__name__]
            current = current.get(name)
        return current


def extract_date(str):
    if not str:
        return datetime.datetime.now(pytz.UTC)
    date = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return date.replace(tzinfo=pytz.UTC)

def fix_relative_links(document, current_path):

    def fix_relative(url):
        if not url.startswith('/'):
            return
        return bn.relpath(url, current_path)

    return asm.cms.utils.rewrite_urls(document, fix_relative)
