import grok
import zope.interface


class MainSponsorBox(grok.View):
    grok.context(zope.interface.Interface)
