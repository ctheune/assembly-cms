# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.name('edit')

    main_fields = grok.AutoFields(Asset).select(
        'title', 'content')
    main_fields['content'].custom_widget = FileWithDisplayWidget


class ImagePicker(grok.View):
    grok.context(Asset)
    grok.name('image-picker')

