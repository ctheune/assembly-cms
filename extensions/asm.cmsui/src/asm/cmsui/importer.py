# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.cmsui.form
import asm.cmsui.base
import zope.interface
import asm.cms.cms

class ImportActions(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.base.NavigationToolActions)
    grok.context(zope.interface.Interface)


class Import(asm.cmsui.form.Form):

    grok.context(asm.cms.cms.CMS)
    form_fields = grok.AutoFields(asm.cms.interfaces.IImport)

    @grok.action(u'Import')
    def import_action(self, data):
        importer = asm.cms.Importer(self.context, data)
        importer()
