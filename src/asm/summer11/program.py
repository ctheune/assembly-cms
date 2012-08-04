import asm.cms.edition
import asm.cmsui.retail
import asm.party.program
import asm.summer11.skin
import grok


class ProgramIndex(asm.cmsui.retail.Pagelet):

    grok.name('index')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.ProgramSection)

    def events(self):
        for page in self.context.page.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition


class SectionSnippet(grok.View):

    grok.name('snippet')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.ProgramSection)

    def sub(self, context=None):
        if context is None:
            context = self.context
        for page in context.page.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition


class CompetitionSnippet(grok.View):

    grok.name('snippet')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.Competition)


class EventSnippet(grok.View):

    grok.name('snippet')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.Event)
