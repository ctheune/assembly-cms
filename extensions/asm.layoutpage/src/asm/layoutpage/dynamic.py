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


class BaseUrl(grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def render(self):
        return self.application_url()
