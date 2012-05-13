import grok
import zope.interface


class SponsorBox(grok.View):
    grok.context(zope.interface.Interface)

    randomize = True
    category = 'sponsor'
    limit = 4

    def sponsors(self):
        return self.view('choosebanner').choose(
                self.category, self.limit, randomize=self.randomize)


class MainSponsorBox(SponsorBox):
    grok.template('sponsorbox')

    randomize = False
    category = 'main'
    limit = None


class AssociateBox(SponsorBox):
    grok.template('sponsorbox')

    category = 'associate'
    limit = 2
