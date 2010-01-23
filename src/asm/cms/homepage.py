# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms
import asm.cms.edition
import grok
import zope.interface


class Homepage(asm.cms.Edition):
    """A homepage based on a disk-template."""

    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Homepage'


class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')
