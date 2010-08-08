# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt



class ImportActions(grok.Viewlet):

    grok.viewletmanager(asm.cms.NavigationToolActions)
    grok.context(zope.interface.Interface)


class Import(asm.cms.Form):

    grok.context(asm.cms.cms.CMS)
    form_fields = grok.AutoFields(IImport)

    @grok.action(u'Import')
    def import_action(self, data):
        importer = asm.cms.Importer(self.context, data)
        importer()
