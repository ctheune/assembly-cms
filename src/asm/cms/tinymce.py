# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.form.browser.textwidgets
import hurry.tinymce.tinymce
import hurry.resource

widget_lib = hurry.resource.Library('asm.cms')
widget = hurry.resource.ResourceInclusion(widget_lib, 'tinymce_widget.js',
                                 depends=[hurry.tinymce.tinymce])


class TinyMCEWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        widget.need()
        self.cssClass += ' mceEditor'
        return super(TinyMCEWidget, self).__call__()
