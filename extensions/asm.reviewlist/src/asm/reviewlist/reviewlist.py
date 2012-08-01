from BTrees.LOBTree import LOBTree
import asm.cms.interfaces
import asm.cmsui.base
import datetime
import grok
import logging
import megrok.pagelet
import persistent
import time
import zope.interface
import zope.intid.interfaces
import zope.traversing.api


log = logging.getLogger('asm.reviewlist')


class Reviewlist(megrok.pagelet.Pagelet):

    grok.context(asm.cms.interfaces.ICMS)
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        changelog = zope.component.getUtility(IChangeLog)
        self.changes = changelog.get_changes()


class Menuitem(grok.Viewlet):
    grok.viewletmanager(asm.cmsui.base.HeaderActions)
    grok.context(zope.interface.Interface)


class Change(persistent.Persistent):

    timestamp = None  # datetime.datetime
    user_id = None  # username
    object_id = None  # intid of changed object

    @property
    def object(self):
        intids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
        return intids.getObject(self.object_id)


class IChangeLog(zope.interface.Interface):

    def record_change(object):
        """Record the fact that this object was changed "now"."""

    def get_changes(limit=50):
        """Return the last "limit" changes. Newest first."""


class ChangeLog(grok.LocalUtility):

    grok.implements(IChangeLog)

    def __init__(self):
        super(ChangeLog, self).__init__()
        self.changes = LOBTree()

    def record_change(self, object):
        request = zope.security.management.getInteraction().participations[0]
        intids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
        change = Change()
        change.timestamp = datetime.datetime.now()
        change.user_id = request.principal.title
        change.object_id = intids.register(object)
        key = int(time.mktime(change.timestamp.timetuple())*1000)
        self.changes[key] = change

    def get_changes(self, limit=50):
        return reversed(self.changes.values()[-limit:])


def install_utility(cms):
    sm = zope.component.getSiteManager(cms)
    sm['changelog'] = ChangeLog()
    sm.registerUtility(sm['changelog'], IChangeLog)


@grok.subscribe(asm.cms.interfaces.ICMS, grok.IObjectAddedEvent)
def install_utility_when_adding_site(cms, event):
    install_utility(cms)


@grok.subscribe(asm.cms.interfaces.IEdition, grok.IObjectModifiedEvent)
def register_change(edition, event):
    try:
        changelog = zope.component.getUtility(IChangeLog)
    except:
        path = zope.traversing.api.getPath(edition)
        log.warn("No changelog utility installed near %s. "
                 "Not recording change." % path)
    else:
        changelog.record_change(event.object)
