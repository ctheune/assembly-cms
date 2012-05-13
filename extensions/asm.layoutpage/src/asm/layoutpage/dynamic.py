import grok
import asm.cms.interfaces
import asm.cmsui.interfaces
import asm.cms.edition


class TileNavigation(grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def update(self):
        self.rows = []
        row = []
        for edition in asm.cms.edition.find_editions(self.context.page, self.request,
                recurse=False):
            if edition.has_tag('hide-navigation'):
                continue
            if len(row) == 3:
                self.rows.append(row)
                row = []
            row.append(edition)

        self.rows.append(row)


class SectionNavigation(grok.View):
    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def find_section(self):
        candidate = self.context
        while candidate != self.application:
            if candidate.__parent__ == self.application:
                return candidate
            candidate = candidate.__parent__

    def update(self):
        self.section = self.find_section()
        self.subsections = []
        for edition in asm.cms.edition.find_editions(self.section, self.request,
                recurse=False):
            if edition.has_tag('hide-navigation'):
                continue
            self.subsections.append(edition)


class BaseUrl(grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def render(self):
        return self.application_url()



