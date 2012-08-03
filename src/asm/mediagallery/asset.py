# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import asm.cms.asset
import asm.cmsui.base


class ViewGallery(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.asset.Asset)
