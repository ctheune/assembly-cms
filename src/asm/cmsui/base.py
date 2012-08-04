import asm.cmsui.interfaces
import grok
import zope.interface


class ActionView(grok.View):

    grok.baseclass()
    grok.layer(asm.cmsui.interfaces.ICMSSkin)

    def render(self):
        self.redirect(self.url(self.context, '@@edit'))


class PageHeader(grok.ViewletManager):
    grok.context(zope.interface.Interface)
    grok.name('pageheader')


class HeaderActions(grok.ViewletManager):

    grok.name('header-actions')
    grok.context(zope.interface.Interface)


class MainPageActions(grok.ViewletManager):

    grok.name('main-page-actions')
    grok.context(zope.interface.Interface)


class ExtendedPageActions(grok.ViewletManager):

    grok.name('extended-page-actions')
    grok.context(zope.interface.Interface)


class PageActionGroups(grok.ViewletManager):

    grok.name('page-action-groups')
    grok.context(zope.interface.Interface)


class NavigationActions(grok.ViewletManager):

    grok.name('navigation-actions')
    grok.context(zope.interface.Interface)


class NavigationToolActions(grok.ViewletManager):

    grok.name('navigation-tool-actions')
    grok.context(zope.interface.Interface)


class NotificationMessages(grok.ViewletManager):

    grok.context(zope.interface.Interface)
    grok.name('notification-messages')
