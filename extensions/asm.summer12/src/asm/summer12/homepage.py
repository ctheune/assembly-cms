# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
from asm.cms.homepage import Homepage
from .skin import ISkin, PageContent


class Index(grok.Viewlet):
    grok.context(Homepage)
    grok.viewletmanager(PageContent)
    grok.layer(ISkin)
