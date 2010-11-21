# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import zope.interface
import grok


class ProgramSection(asm.cms.edition.Edition):

    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Program section'


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


class EditCompetition(asm.cmsui.form.EditionEditForm):

    grok.context(Competition)
    main_fields = grok.AutoFields(asm.party.interfaces.ICompetition)


class MusicEvent(asm.cms.edition.Edition):

    zope.interface.classProvides(asm.cms.interfaces.IEditionFactory)

    factory_title = u'Music event'
    factory_visible = True
    factory_enabled = staticmethod(
        lambda parent:parent.factory is ProgramSection)
