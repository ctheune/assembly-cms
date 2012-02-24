# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.blob
import asm.cms
import asm.cms.cms
import asm.cms.edition
import asm.cms.htmlpage
import base64
import datetime
import grok
import lxml.etree
import pytz
import zope.exceptions.interfaces
import zope.interface
import zope.schema
import zope.traversing.api

def base64_to_blob(data):
    value = ZODB.blob.Blob()
    f = value.open('w')
    f.write(base64.decodestring(data))
    f.close()
    return value

class ImportError(ValueError):
    pass


class Importer(object):
    """Import content from an XML file.


    """

    def __init__(self, cms, data):
        self.cms = cms
        self.data = data

    def __call__(self, allow_duplicates=False):
        errors = []
        try:
            export = lxml.etree.fromstring(self.data)
        except lxml.etree.XMLSyntaxError, e:
            return ["XML syntax error: %s." % e]
        self.base_path = export.get('base')
        for page_node in export:
            page_path = page_node.get('path')
            page = self.get_page(page_path, page_node.tag)

            if page_node.get('purge', 'false').lower() == 'true':
                for subpage in list(page.subpages):
                    del page[subpage.__name__]
                for edition in list(page.editions):
                    del page[edition.__name__]

            for edition_node in page_node:
                assert edition_node.tag == 'edition'
                parameters_value = edition_node.get('parameters')
                parameters = set(parameters_value.split())
                parameters = asm.cms.edition.EditionParameters(parameters)
                if 'lang:' in parameters:
                    # ensure that the fallback language is english
                    parameters = parameters.replace('lang:', 'lang:en')
                try:
                    edition = page.addEdition(parameters)
                except KeyError:
                    # Leave existing content alone.
                    if not allow_duplicates:
                        errors.append(
                            "Duplicate page '%s' with edition '%s' detected" % (
                                page_path, parameters_value))
                    continue
                getattr(self, 'import_%s' % page.type)(edition, edition_node)
                edition.title = edition_node.get('title')
                edition.tags = edition_node.get('tags')
                edition.modified = extract_date(edition_node.get('modified'))
                edition.created = extract_date(edition_node.get('created'))
                zope.event.notify(grok.ObjectModifiedEvent(edition))
        zope.event.notify(ContentImported(self.cms, errors))
        return errors

    def import_htmlpage(self, edition, node):
        content = base64.decodestring(node.text).decode('utf-8')
        asm.cms.htmlpage.fix_relative_links(
            content, self.base_path + '/' + node.getparent().get('path'))
        edition.content = content

    def import_asset(self, edition, node):
        edition.content = base64_to_blob(node.text)

    def get_page(self, path, type_):
        path = path.split('/')
        current = self.cms
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


class ContentImported(object):

    zope.interface.implements(asm.cms.interfaces.IContentImported)

    def __init__(self, site, errors):
        self.site = site
        self.errors = errors


def extract_date(str):
    if not str:
        return datetime.datetime.now(pytz.UTC)
    date = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return date.replace(tzinfo=pytz.UTC)
