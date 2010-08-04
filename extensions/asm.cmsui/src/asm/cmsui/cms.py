# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class PreviewWindow(grok.View):

    grok.name('preview-window')
    grok.template('preview-window')

class SelectProfile(asm.cms.form.EditForm):

    form_fields = grok.AutoFields(IProfileSelection)

