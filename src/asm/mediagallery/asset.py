import asm.cms.asset
import asm.cmsui.base
import grok


class ViewGallery(asm.cmsui.retail.Pagelet):

    grok.context(asm.cms.asset.Asset)
