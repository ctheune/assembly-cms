# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.page
import grok
import zope.component
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser


class CMS(grok.Application, asm.cms.page.Page):

    zope.interface.implements(asm.cms.interfaces.ICMS)

    type = 'htmlpage'


class PreviewWindow(grok.View):

    grok.name('preview-window')
    grok.template('preview-window')
