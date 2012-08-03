import grok
import datetime
import whenIO


class DateFormat(grok.View):

    grok.context(datetime.datetime)
    grok.name('format')

    def render(self):
        # XXX L10N or simple 'XXX time ago'
        return self.context.strftime('%d.%m.%Y %H:%M')

    def when(self):
        w = whenIO.WhenIO()
        return w.format(self.context)


class NoneFormat(grok.View):
    grok.name('format')
    grok.context(None.__class__)

    def render(self):
        return ''
