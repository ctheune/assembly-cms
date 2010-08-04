# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class Edit(asm.cms.EditForm):

    grok.context(NewsFolder)

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')
