# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.form.browser.textwidgets
import hurry.tinymce.tinymce
import hurry.resource
import asm.cms.interfaces
import grok

widget_lib = hurry.resource.Library('asm.cmsui')
widget = hurry.resource.ResourceInclusion(widget_lib, 'tinymce_widget.js',
                                 depends=[hurry.tinymce.tinymce],
                                 bottom=True)

popup = hurry.resource.ResourceInclusion(
    hurry.tinymce.tinymce_lib, 'tiny_mce_popup.js')


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

    def __call__(self):
        popup.need()
        return super(TinyMCELinkBrowser, self).__call__()

    def pages(self):
        # Return a set of editions representing the pages
        for page in self.context.subpages:
            yield asm.cms.edition.select_edition(page, self.request)

    def breadcrumbs(self):
        result = []
        current = self.context
        while True:
            result.insert(0,
                asm.cms.edition.select_edition(current, self.request))
            if current is self.application:
                break
            current = current.__parent__
        return result
