# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt



class Edit(asm.cms.EditForm):

    grok.context(NewsFolder)

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')


class Index(asm.cms.Pagelet):

    grok.context(NewsFolder)

    def list(self):
        for news in self.context.list():
            edition = asm.cms.edition.select_edition(news, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition
