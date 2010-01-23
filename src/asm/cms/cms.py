# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.page
import grok
import zope.component
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser
import zope.app.intid.interfaces


class CMS(grok.Application, asm.cms.page.Page):

    zope.interface.implements(asm.cms.interfaces.ICMS)

    type = 'htmlpage'


@grok.subscribe(zope.app.intid.interfaces.IIntIds, grok.IObjectAddedEvent)
def cleanup_initial_edition(obj, event):
    # This is a work-around for an ordering problem: eventually the initial
    # editions are created before the intid utility is registered. This cleans
    # up that mess and registeres all editions that exist in the CMS directly.
    cms = obj.__parent__.__parent__
    if not asm.cms.interfaces.ICMS.providedBy(cms):
        return
    for edition in cms.values():
        obj.register(edition)


class PreviewWindow(grok.View):

    grok.name('preview-window')
    grok.template('preview-window')
