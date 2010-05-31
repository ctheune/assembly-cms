# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import z3c.baseregistry.baseregistry
import zc.sourcefactory.basic
import asm.cms.page
import grok
import zope.component
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser
import zope.app.intid.interfaces


class CMS(grok.Application, asm.cms.page.Page):

    zope.interface.implements(asm.cms.interfaces.ICMS)

    # Keep this here to support old instances.
    type = 'htmlpage'

    def __init__(self, type='htmlpage'):
        super(CMS, self).__init__(type)


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
    obj.register(cms)


class PreviewWindow(grok.View):

    grok.name('preview-window')
    grok.template('preview-window')


class ProfileSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return [name for name, profile in
                zope.component.getUtilitiesFor(asm.cms.interfaces.IProfile)]


class IProfileSelection(zope.interface.Interface):

    name = zope.schema.Choice(
        title=u'Profile',
        source=ProfileSource())


class CMSProfile(grok.Adapter):
    grok.context(CMS)
    grok.provides(IProfileSelection)

    def set_name(self, value):
        value = zope.component.getUtility(asm.cms.interfaces.IProfile,
                                          name=value)
        sm = self.context.getSiteManager()
        bases = (x for x in sm.__bases__
                 if not asm.cms.interfaces.IProfile.providedBy(x))
        sm.__bases__ = (value,) + tuple(bases)

    def get_name(self):
        sm = self.context.getSiteManager()
        for profile in sm.__bases__:
            if not asm.cms.interfaces.IProfile.providedBy(profile):
                continue
            break
        else:
            return None
        for name, reg_profile in zope.component.getUtilitiesFor(
                asm.cms.interfaces.IProfile):
            if reg_profile is profile:
                return name

    name = property(fget=get_name, fset=set_name)


class SelectProfile(asm.cms.form.EditForm):

    form_fields = grok.AutoFields(IProfileSelection)


class Profile(z3c.baseregistry.baseregistry.BaseComponents):

    zope.interface.implements(asm.cms.interfaces.IProfile)

    def __init__(self, name):
        super(Profile, self).__init__(zope.component.globalSiteManager, name)
