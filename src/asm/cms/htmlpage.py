# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.form
import asm.cms.interfaces
import asm.cms.tinymce
import grok
import megrok.pagelet
import zope.interface


class HTMLPage(asm.cms.edition.Edition):

    zope.interface.implements(asm.cms.interfaces.IHTMLPage)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    _content = u''
    def content():
        def fget(self):
            return self._content

        def fset(self,value):
            self._content = value
            self._title=scrape_title(value)
        return locals()
    content = property(**content())

    _title = u''
    def title():
        doc="Title that cannot be mutated"
        def fget(self):
            return self._title

        def fset(self,value):
            # Don't accept new titles this way!
            pass #XXX or raise?
        return locals()
    title = property(**title())

    def copyFrom(self, other):
        # NB. This will magically update self.title as well.
        self.content = other.content


class Index(megrok.pagelet.Pagelet):
    pass


class Edit(asm.cms.form.EditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)

    form_fields = reduce(
        lambda x,y: x.omit(y),
        ['parameters','title','tags','date_created','date_modified'],
        grok.AutoFields(HTMLPage))
    form_fields['content'].custom_widget = asm.cms.tinymce.TinyMCEWidget
