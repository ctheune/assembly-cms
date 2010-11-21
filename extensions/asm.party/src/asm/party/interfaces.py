# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.interfaces
import zope.schema


class IProgramSection(zope.interface.Interface):

    title = zope.schema.TextLine(title=u'Title')

    headline = zope.schema.TextLine(title=u'Headline')


class ICompetition(zope.interface.Interface):

    title = zope.schema.TextLine(title=u'Title')

    headline = zope.schema.TextLine(title=u'Headline')

    description = zope.schema.Text(
        title=u'Description',
        description=u'Describe what the competition is about. What makes '
                    u'it different from other competitions? What should the '
                    u'audience expect? This needs to fit in 2-3 paragraphs.')

    location = zope.schema.TextLine(title=u'Location', required=False)

    time = zope.schema.Datetime(title=u'Time', required=False)

    prizes = zope.schema.TextLine(title=u'Prizes', required=False)

    participation_info = zope.schema.URI(
        title=u'Link to more information for participants (rules, deadlines etc.)',
        required=False)

    gallery = zope.schema.URI(
        title=u'Link to a gallery for this competition', required=False)
