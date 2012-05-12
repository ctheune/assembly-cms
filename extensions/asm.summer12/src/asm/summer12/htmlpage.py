# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from .skin import ISkin, EmbeddedPageContent
from asm.cms.htmlpage import HTMLPage
import grok


class Embedded(grok.Viewlet):
    grok.layer(ISkin)
    grok.context(HTMLPage)
    grok.viewletmanager(EmbeddedPageContent)
    grok.template('embedded')
