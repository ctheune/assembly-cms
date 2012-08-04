import asm.cms
import asm.cms.edition
import zope.interface


class Homepage(asm.cms.Edition):
    """A homepage based on a disk-template."""

    zope.interface.classProvides(asm.cms.IEditionFactory)

    factory_title = u'Homepage'
