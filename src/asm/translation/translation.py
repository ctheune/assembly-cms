# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.form
import asm.cms.interfaces
import grok
import zope.interface
import zope.schema


@grok.subscribe(asm.cms.interfaces.IInitialVariationCreated)
def set_initial_language(event):
    event.variation.parameters.insert('lang:en')


@zope.component.adapter(asm.cms.interfaces.IRetailSkin)
def select_retail_variation(request):
    for lang in request.headers.get('Accept-Language', '').split(','):
        lang = lang.split(';')[0]
        lang = lang.split('-')[0]
        lang = 'lang:%s' % lang
        return set([lang])
    return set(['lang:en'])


class ITranslation(zope.interface.Interface):

    language = zope.schema.Choice(title=u'Language to translate to',
                                  values=['fi'])


class TranslationMenu(grok.Viewlet):
    grok.viewletmanager(asm.cms.location.Actions)
    grok.context(asm.cms.interfaces.IVariation)


class Translate(asm.cms.form.Form):

    grok.context(asm.cms.interfaces.IVariation)
    form_fields = grok.AutoFields(ITranslation)

    @grok.action(u'Translate')
    def translate(self, language):
        parameters = set()
        for parameter in self.context.parameters:
            if parameter.startswith('lang:'):
                continue
            parameters.add(parameter)
        parameters.add('lang:%s' % language)
        location = self.context.__parent__
        try:
            variation = location.getVariation(parameters)
        except KeyError:
            variation = location.addVariation(parameters)
            variation.copyFrom(self.context)
            self.flash(u'Created translation.')
        else:
            self.flash(u'Translation already exists.')
