# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import asm.party.interfaces
import zope.interface
import grok


class ProgramSection(asm.cms.edition.Edition):

    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)
    zope.interface.implements(asm.party.interfaces.IProgramSection)

    factory_title = u'Program section'

    headline = u''


class EditSection(asm.cmsui.form.EditionEditForm):

    grok.context(asm.party.interfaces.IProgramSection)
    main_fields = grok.AutoFields(asm.party.interfaces.IProgramSection)
    grok.name('edit')


class Competition(asm.cms.edition.Edition):

    zope.interface.implements(asm.party.interfaces.ICompetition)
    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Competition'
    factory_visible = True
    factory_enabled = staticmethod(
        lambda parent:parent.factory is ProgramSection)

    headline = u''
    description = u''
    location = u''
    time = None
    prizes = u''
    participation_info = None
    gallery = None

    def copyFrom(self, other):
        super(Competition, self).copyFrom(other)
        self.headline = other.headline
        self.description = other.description
        self.location = other.location
        self.time = other.time
        self.prizes = other.prizes
        self.participation_info = other.participation_info
        self.gallery = other.gallery


class EditCompetition(asm.cmsui.form.EditionEditForm):

    grok.context(Competition)
    main_fields = grok.AutoFields(asm.party.interfaces.ICompetition)


class MusicEvent(asm.cms.edition.Edition):

    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Music event'
    factory_visible = True
    factory_enabled = staticmethod(
        lambda parent:parent.factory is ProgramSection)
