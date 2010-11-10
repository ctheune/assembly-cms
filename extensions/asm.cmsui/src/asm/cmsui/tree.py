# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cmsui.interfaces
import cgi
import grok
import StringIO
import zope.component

STATE_CLOSED = False
STATE_OPEN = True
STATE_NONE = None

class Tree(grok.View):

    grok.context(grok.Application)   # XXX Meh.
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    parent = None
    open_page = None

    def update(self, parent_id=None, page_id=None):
        self.request.response.setHeader('Content-Type', 'text/xml')
        if parent_id is None:
            self.parent = self.context
        else:
            iids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
            parent = iids.getObject(int(parent_id))
            self.parent = parent

        # Page ID is used to give enough data in initial tree that the branch
        # that has currently open page is also transmitted in the initial
        # data request.
        if page_id is not None:
            iids = zope.component.getUtility(zope.app.intid.interfaces.IIntIds)
            page = iids.getObject(int(page_id))
            self.open_page = page

    def _get_page_data(self, page):
        intids = zope.component.getUtility(zope.app.intid.IIntIds)
        edition = asm.cms.edition.select_edition(page, self.request)

        if isinstance(edition, asm.cms.edition.NullEdition):
            ref = page
            title = page.__name__
        else:
            ref = edition
            title = edition.title

        page_id = intids.getId(page)
        if title is None:
            title = u''

        state = STATE_NONE
        if len(list(page.subpages)) > 0:
            state = STATE_CLOSED

        parent_id = None
        if page != self.context:
            parent_id = intids.getId(page.__parent__)

        return {
            'rel': page.type,
            'id': page_id,
            'parent_id': parent_id,
            'state': state,
            'url': self.url(ref),
            'title': title,
            }

    def _page_to_xml(self, page):
        parent_str = ""
        if page['parent_id'] is not None:
            parent_str = 'parent_id="%s"' % page['parent_id']

        state_str = ""
        if page['state'] is not STATE_NONE:
            if page['state'] == STATE_OPEN:
                state_str = 'state="open"'
            elif page['state'] == STATE_CLOSED:
                state_str = 'state="closed"'

        return """<item rel="%(rel)s" %(parent_str)s id="%(id)s" %(state_str)s>
<content><name href="%(url)s">%(title)s</name></content>
</item>
""" % {'rel': page['rel'],
       'parent_str': parent_str,
       'id': page['id'],
       'state_str': state_str,
       'url': page['url'],
       'title': cgi.escape(page['title'].encode('utf8'))
       }

    def _sub_pages(self, parent):
        pages = []
        for sub in parent.subpages:
            pages.append(self._get_page_data(sub))
        return pages

    def _open_branches_leading_to_open_page(self, pages):
        # TODO maybe some cleanups
        opened_ids = []
        open_page = self.open_page
        intids = zope.component.getUtility(zope.app.intid.IIntIds)
        while open_page is not None and self.context != open_page:
            pages.extend(self._sub_pages(open_page))
            open_page = open_page.__parent__
            if open_page is not None:
                opened_ids.append(intids.getId(open_page))

        for page in pages:
            if page['id'] in opened_ids:
                page['state'] = STATE_OPEN

        return pages

    def tree(self):
        pages = self._sub_pages(self.parent)

        pages = self._open_branches_leading_to_open_page(pages)

        result = StringIO.StringIO()
        result.write("<root>\n")
        for page in pages:
            result.write(self._page_to_xml(page))
        result.write("</root>\n")

        return result.getvalue()
