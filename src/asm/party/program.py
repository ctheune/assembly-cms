import asm.cms.edition
import asm.cms.interfaces
import asm.cmsui.tinymce
import asm.party.interfaces
import grok
import zope.interface


class ProgramSection(asm.cms.edition.Edition):

    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)
    zope.interface.implements(asm.party.interfaces.IProgramSection)

    factory_title = u'Program section'

    description = u''
    headline = u''


class EditSection(asm.cmsui.form.EditionEditForm):

    grok.context(asm.party.interfaces.IProgramSection)
    main_fields = grok.AutoFields(asm.party.interfaces.IProgramSection)
    main_fields['description'].custom_widget = asm.cmsui.tinymce.TinyMCEWidget
    grok.name('edit')


class Event(asm.cms.edition.Edition):

    zope.interface.implements(asm.party.interfaces.IEvent)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Event'
    factory_visible = staticmethod(
        lambda parent: parent.factory is ProgramSection)

    headline = u''
    description = u''
    location = u''
    time = None

    def copyFrom(self, other):
        super(Event, self).copyFrom(other)
        self.headline = other.headline
        self.description = other.description
        self.location = other.location
        self.time = other.time


class EditEvent(asm.cmsui.form.EditionEditForm):

    grok.context(Event)
    main_fields = grok.AutoFields(asm.party.interfaces.IEvent)


class Competition(asm.cms.edition.Edition):

    zope.interface.implements(asm.party.interfaces.ICompetition)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Competition'
    factory_visible = staticmethod(
        lambda parent: parent.factory is ProgramSection)

    prizes = u''
    participation_info = None
    gallery = None

    def copyFrom(self, other):
        super(Competition, self).copyFrom(other)
        self.prizes = other.prizes
        self.participation_info = other.participation_info
        self.gallery = other.gallery


class EditCompetition(asm.cmsui.form.EditionEditForm):

    grok.context(Competition)
    main_fields = grok.AutoFields(asm.party.interfaces.ICompetition)
