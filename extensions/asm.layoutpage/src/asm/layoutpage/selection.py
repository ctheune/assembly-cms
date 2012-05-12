import asm.cms.edition
import asm.layoutpage.interfaces
import grok
import zc.sourcefactory.contextual
import zope.interface
import zope.schema


class LayoutSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getValues(self, context):
        layouts = zope.component.getUtilitiesFor(
            asm.layoutpage.interfaces.ILayoutPage, context=context)
        return [layout[0] for layout in layouts]

    def getTitle(self, context, value):
        if value == '':
            return 'default'
        return value


class ILayoutSelection(zope.interface.Interface):

    zope.interface.taggedValue('label', u'Layout')
    zope.interface.taggedValue(
        'description', u'Select a page layout to use when displaying this page.')

    layout = zope.schema.Choice(
        title=u'Layout',
        source=LayoutSource())




class LayoutAnnotation(grok.Annotation):
    grok.implements(ILayoutSelection)
    grok.provides(ILayoutSelection)
    grok.context(asm.cms.interfaces.IEdition)

    layout = ''

    def copyFrom(self, other):
        self.layout = other.layout

    def __eq__(self, other):
        return self.layout == other.layout

    def get_layout(self, request):
        layout = zope.component.getUtility(
            asm.layoutpage.interfaces.ILayoutPage, name=self.layout)
        # Special case: the layout might be a page. We then run
        # select_edition to get the actual thing.
        if asm.cms.interfaces.IPage.providedBy(layout):
            layout = asm.cms.edition.select_edition(layout, request)
        return layout


def add_layout_data(edition):
    if asm.layoutpage.interfaces.ILayoutPage.providedBy(edition):
        return
    return ILayoutSelection
