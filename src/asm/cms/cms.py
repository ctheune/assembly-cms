# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.page
import grok


class CMS(grok.Application, asm.cms.page.Page):

    type = 'htmlpage'

