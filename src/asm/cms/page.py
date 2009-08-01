# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet


class Page(grok.Container):

    content = u''


class Index(megrok.pagelet.Pagelet):
    pass
