# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class Tree(grok.View):

    grok.context(grok.Application)   # XXX Meh.
    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.request.response.setHeader('Content-Type', 'text/xml')

    def _sub_projects(self, root):
        intids = zope.component.getUtility(zope.app.intid.IIntIds)
        edition = asm.cms.edition.select_edition(root, self.request)
        if isinstance(edition, asm.cms.edition.NullEdition):
            ref = root
            title = root.__name__
        else:
            ref = edition
            title = edition.title

        id = intids.getId(root)

        html = '<item rel="%s" id="%s">\n' % (
            root.type, id)
        html += '<content><name href="%s">%s</name></content>\n' % (
            self.url(ref), cgi.escape(title))
        for sub in root.subpages:
            html += self._sub_projects(sub)
        html += "</item>\n"
        return html

    def tree(self):
        html = "<root>\n%s" % self._sub_projects(self.context)
        html += "</root>\n"
        return html
