# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.edition
import grok
import zope.interface


class Homepage(asm.cms.Edition):
    """A homepage based on a disk-template."""

    zope.interface.classProvides(asm.cms.IEditionFactory)


class Edit(asm.cms.EditForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title', 'tags', 'modified')
    form_fields['tags'].location = 'side'
    form_fields['modified'].location = 'side'
