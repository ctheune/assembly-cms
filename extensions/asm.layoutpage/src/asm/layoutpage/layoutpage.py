import asm.cms
import asm.cms.utils
import asm.cmsui.retail
import asm.cmsui.form
import asm.layoutpage.interfaces
import grok
import zope.interface
import re


class LayoutPage(asm.cms.Edition):
    """A layout page provides a way to enter pure HTML with a simple set of
    variable expansions to insert content from sub-page elements at run-time.
    """

    zope.interface.classProvides(asm.cms.IEditionFactory)
    zope.interface.implements(asm.layoutpage.interfaces.ILayoutPage)

    factory_title = u'Layout page'
    layout = u''

    def copyFrom(self, other):
        super(LayoutPage, self).copyFrom(other)
        self.layout = other.layout

    def _lookup(self, name, request, partial_render):
        page = self.page[name]
        edition = asm.cms.edition.select_edition(page, request)
        return partial_render(request, edition)

    def render(self, request, partial_render):
        template = LayoutTemplate(
            self.layout, lambda name:self._lookup(name, request,
                partial_render))
        return template()


class LayoutTemplate(object):

    MARKER_PATTERN = re.compile('\${(.*?)}')

    def __init__(self, template, value_lookup):
        self.template = template
        self.value_lookup = value_lookup

    def __call__(self):
        return self.MARKER_PATTERN.sub(
            lambda match:self.value_lookup(match.groups()[0]),
            self.template)


class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    main_fields = grok.AutoFields(LayoutPage).select('title', 'layout')
