import asm.cms
import asm.cms.utils
import asm.cmsui.form
import asm.cmsui.retail
import asm.layoutpage.interfaces
import grok
import re
import zope.interface
import zope.traversing.interfaces


class Layout(object):

    zope.interface.implements(asm.layoutpage.interfaces.ILayoutPage)

    layout = u''

    def _lookup(self, name, request, context, partial_render):
        # ${}
        if name == '':
            return partial_render(request, context)
        elif name.startswith('@@'):
            name = name.replace('@@', '')
            return zope.component.getMultiAdapter(
                    (context, request), name=name)()
        else:
            # ${subitemname} or ${subitem/foo} or ${/asdf}
            root = context.page
            if name.startswith('/'):
                name = name[1:]
                root = grok.util.getApplication()
            traverser = zope.traversing.interfaces.ITraverser(root)
            page = traverser.traverse(name)
            target = asm.cms.edition.select_edition(page, request)
            return partial_render(request, target)
        raise RuntimeError("Invalid lookup: %r" % name)

    def render(self, request, context, partial_render):
        template = LayoutTemplate(
            self.layout, lambda name: self._lookup(
                name, request, context, partial_render))
        return template()


class LayoutPage(asm.cms.Edition, Layout):
    """A layout page provides a way to enter pure HTML with a simple set of
    variable expansions to insert content from sub-page elements at run-time.
    """

    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Layout page'
    layout = u''

    def copyFrom(self, other):
        super(LayoutPage, self).copyFrom(other)
        self.layout = other.layout


class LayoutTemplate(object):

    MARKER_PATTERN = re.compile('\${(.*?)}')

    def __init__(self, template, value_lookup):
        self.template = template
        self.value_lookup = value_lookup

    def __call__(self):
        return self.MARKER_PATTERN.sub(
            lambda match: self.value_lookup(match.groups()[0]),
            self.template)


class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    main_fields = grok.AutoFields(LayoutPage).select('title', 'layout')


@grok.subscribe(LayoutPage, grok.IObjectAddedEvent)
def ensure_page_is_local_utility(obj, event):
    page = obj.page
    # Check whether it's OK to register the layoutpage with the given name.
    try:
        registered_page = zope.component.getUtility(
            asm.layoutpage.interfaces.ILayoutPage, name=page.__name__)
    except LookupError:
        # Nothing registered with this name -> OK
        pass
    else:
        if isinstance(registered_page, asm.layoutpage.layouts.DefaultLayout):
            # The registered page is the global default page -> OK
            pass
        elif registered_page is not page:
            raise KeyError('Layout page with this name already exists.')
    # Alright, nothing is stopping us from registering it with the given name.
    sm = zope.component.getSiteManager(obj)
    sm.registerUtility(page,
         provided=asm.layoutpage.interfaces.ILayoutPage, name=page.__name__)


@grok.subscribe(asm.cms.interfaces.IPage, grok.IObjectRemovedEvent)
def ensure_page_is_not_local_utility(obj, event):
    try:
        zope.component.getUtility(
            asm.layoutpage.interfaces.ILayoutPage, name=obj.__name__)
    except LookupError:
        pass
    else:
        sm = zope.component.getSiteManager(obj)
        unregistered = sm.unregisterUtility(obj,
             provided=asm.layoutpage.interfaces.ILayoutPage, name=obj.__name__)
        if not unregistered:
            raise RuntimeError('Layout page not registered?!')
