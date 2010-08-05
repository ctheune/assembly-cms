# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.cms.cms
import asm.cmsui.form


grok.context(asm.cms.cms.CMS)


class PreviewWindow(grok.View):

    grok.name('preview-window')
    grok.template('preview-window')


class SelectProfile(asm.cmsui.form.EditForm):

    # XXX why does iprofileselection live in asm.cms.cms?
    form_fields = grok.AutoFields(asm.cms.cms.IProfileSelection)

