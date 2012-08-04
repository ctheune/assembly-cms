import asm.layoutpage.interfaces
import asm.layoutpage.layoutpage
import grok


class DefaultLayout(asm.layoutpage.layoutpage.Layout, grok.GlobalUtility):
    grok.provides(asm.layoutpage.interfaces.ILayoutPage)
    grok.name('default')

    layout = '${}'
