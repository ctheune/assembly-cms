import asm.cms
import asm.cms.cms
import asm.cms.interfaces
import cgi
import grok
import hashlib
import urllib
import zope.interface


class HTMLReplace(grok.Adapter):
    """Search and replace support for HTML pages."""

    grok.context(asm.cms.interfaces.IHTMLPage)
    grok.implements(asm.cms.interfaces.IReplaceSupport)

    def __init__(self, context):
        self.context = context
        ids = zope.component.getUtility(
            zope.intid.interfaces.IIntIds)
        self.context_id = ids.getId(self.context)

    def search(self, term):
        occurrences = Occurrences()
        for attribute in ['title', 'content']:
            offset = getattr(self.context, attribute).find(term)
            while offset != -1:
                o = Occurrence(self.context, self.context_id,
                              attribute, offset, term)
                occurrences.add(o)
                offset = getattr(self.context, attribute).find(
                    term, offset + 1)
        return occurrences


class Occurrences(object):
    """A helper class to allow multiple occurrences to work on the same
    object and attributes."""

    def __init__(self):
        self.entries = []

    def add(self, occurrence):
        occurrence.group = self
        self.entries.append(occurrence)

    def rebase(self, occurrence, delta):
        """Rebase the offset of all occurrences after occurrence by <delta>
        characters."""
        for candidate in self.entries:
            if candidate.attribute != occurrence.attribute:
                continue
            if candidate.offset <= occurrence.offset:
                continue
            candidate.offset += delta

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)


class Occurrence(object):
    """An occurrence of for search and replace of a term within an HTML
    page."""

    grok.implements(asm.cms.interfaces.IReplaceOccurrence)

    PREVIEW_AMOUNT = 50

    def __init__(self, page, page_id, attribute, offset, term):
        self.page = page
        self.page_id = page_id
        self.attribute = attribute
        self.offset = offset
        self.term = term

        # Only compute the ID initially. Due to rebase behaviour we have to
        # keep the same ID for later replaces that still refer to the old IDs.
        self.set_id()

    def replace(self, target):
        content = getattr(self.page, self.attribute)
        content = (content[:self.offset] + target +
                   content[self.offset + len(self.term):])
        setattr(self.page, self.attribute, content)
        self.group.rebase(self, len(target) - len(self.term))
        zope.event.notify(grok.ObjectModifiedEvent(self.page))

    @property
    def preview(self):
        content = getattr(self.page, self.attribute)
        start = content[max(self.offset - self.PREVIEW_AMOUNT, 0):self.offset]
        end = content[self.offset + len(self.term):
                      self.offset + len(self.term) + self.PREVIEW_AMOUNT]
        return (cgi.escape(start) +
                '<span class="match">' + cgi.escape(self.term) + '</span>' +
                cgi.escape(end))

    def set_id(self):
        content_hash = hashlib.sha1().hexdigest()[:10]
        self.id = '%s-%s-%s-%s' % (self.page_id, content_hash, self.offset,
                                   urllib.quote(self.term.encode('base64')))
