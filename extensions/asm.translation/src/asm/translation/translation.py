# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms
import grok
import zope.interface
import zope.schema


def select_initial_language():
    return set(['lang:en'])


class RetailEditionSelector(object):

    zope.interface.implements(asm.cms.IEditionSelector)
    zope.component.adapts(asm.cms.IPage, asm.cms.IRetailSkin)

    def __init__(self, page, request):
        self.preferred = []

        # We prefer any language the user accepts
        preferred_langs = set()
        for lang in request.headers.get('Accept-Language', '').split(','):
            lang = lang.split(';')[0]
            lang = lang.split('-')[0]
            lang = preferred_langs.add('lang:%s' % lang)
        for edition in page.editions:
            if preferred_langs.intersection(edition.parameters):
                self.preferred.append(edition)

        # Otherwise we also accept language neutral or english
        self.acceptable = []
        for edition in page.editions:
            if 'lang:' in edition.parameters:
                self.acceptable.append(edition)
            if 'lang:en' in edition.parameters:
                self.acceptable.append(edition)


class ITranslation(zope.interface.Interface):

    # Issue #61: Turn static list of values into source.
    language = zope.schema.Choice(title=u'Language to translate to',
                                  values=['fi', 'en'])


class TranslationMenu(grok.Viewlet):

    grok.viewletmanager(asm.cms.Actions)
    grok.context(asm.cms.IEdition)


class Translate(asm.cms.Form):

    grok.context(asm.cms.IEdition)
    form_fields = grok.AutoFields(ITranslation)

    @grok.action(u'Translate')
    def translate(self, language):
        page = self.context.page
        translation = self.context.parameters.replace(
            'lang:*', 'lang:%s' % language)
        try:
            translation = page.getEdition(translation)
        except KeyError:
            translation = page.addEdition(translation)
            translation.copyFrom(self.context)
            self.flash(u'Translation created.')
        else:
            self.flash(u'Translation already exists.')
        self.redirect(self.url(translation, '@@edit'))
