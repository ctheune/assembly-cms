# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.cmsui.form
import asm.cmsui.interfaces
import asm.cms.asset

grok.context(asm.cms.asset.Asset)

class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('edit')

    main_fields = grok.AutoFields(asm.cms.asset.Asset).select(
        'title', 'content')
    main_fields['content'].custom_widget = asm.cmsui.form.FileWithDisplayWidget


class ImagePicker(grok.View):
    grok.name('image-picker')
