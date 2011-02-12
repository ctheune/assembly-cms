# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cmsui.interfaces
import asm.workflow.workflow
import grok
import megrok.pagelet
import zope.app.folder.interfaces
import zope.security.interfaces

grok.context(zope.app.folder.interfaces.IRootFolder)

class Index(megrok.pagelet.Pagelet):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('index.html')
    grok.require('zope.ManageServices')

    def sites(self):
        for obj in self.context.values():
            if asm.cms.interfaces.ICMS.providedBy(obj):
                yield obj

    def skin_name(self, site):
        sm = site.getSiteManager()
        return sm.queryUtility(asm.cms.interfaces.ISkinProfile)


class IndexLayout(megrok.pagelet.Layout):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    megrok.pagelet.template('cmslayout.pt')

    def __call__(self):
        raise zope.security.interfaces.Unauthorized()


class IAddSite(zope.interface.Interface):

    site_name = zope.schema.TextLine(title=u'Site name')


class AddSite(asm.cmsui.form.Form):

    form_fields = (grok.AutoFields(IAddSite) +
                   grok.AutoFields(asm.cms.interfaces.IProfileSelection))

    @grok.action(u'Add')
    def add(self, site_name, name):
        self.context[site_name] = site = asm.cms.cms.CMS()
        profile = asm.cms.interfaces.IProfileSelection(site)
        profile.name = name
        self.redirect(self.url(site))
        ed = site.editions.next()
        ed.content = u'This is the homepage of your new site.'
        ed.title = u'New site'
        asm.workflow.workflow.publish(ed)
