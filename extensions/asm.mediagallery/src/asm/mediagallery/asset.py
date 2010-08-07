# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.cms.asset


class ViewGallery(asm.cms.Pagelet):

    grok.context(asm.cms.asset.Asset)
