# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.cms
import asm.cms.cms
import lxml.etree
import zope.interface
import zope.schema


class Actions(grok.Viewlet):

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
            page_ob.editions.next().content = page.text

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
