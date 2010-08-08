# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt



class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')
