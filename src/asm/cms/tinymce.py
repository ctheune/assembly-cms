# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import zope.app.form.browser.textwidgets
import hurry.tinymce.tinymce
import hurry.resource
import asm.cms.interfaces

widget_lib = hurry.resource.Library('asm.cms')
widget = hurry.resource.ResourceInclusion(widget_lib, 'tinymce_widget.js',
                                 depends=[hurry.tinymce.tinymce],
                                 bottom=True)


class TinyMCEWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        widget.need()
        hurry.resource.bottom(force=True)
        self.cssClass += ' mceEditor'
        return super(TinyMCEWidget, self).__call__()


class TinyMCELinkBrowser(grok.View):

    grok.context(asm.cms.interfaces.IPage)
    grok.name('tinymce-linkbrowser')
    grok.template('linkbrowser')

    def update(self):
        hurry.tinymce.tinymce.need()
