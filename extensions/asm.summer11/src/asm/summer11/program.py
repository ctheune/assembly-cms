# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.party.program
import asm.cmsui.retail
import asm.summer11.skin
import asm.cms.edition
import grok


class ProgramIndex(asm.cmsui.retail.Pagelet):

    grok.name('index')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.ProgramSection)

    def events(self):
        for page in self.context.page.subpages:
            yield asm.cms.edition.select_edition(page, self.request)


class ProgramSectionSnippet(grok.View):

    grok.name('snippet')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.ProgramSection)

    def events(self, subsection):
        for page in self.context.page.subpages:
            edition = asm.cms.edition.select_edition(page, self.request)
            if edition is asm.cms.edition.NullEdition:
                continue


class CompetitionSnippet(grok.View):

    grok.name('snippet')
    grok.layer(asm.summer11.skin.ISkin)
    grok.context(asm.party.program.Competition)
