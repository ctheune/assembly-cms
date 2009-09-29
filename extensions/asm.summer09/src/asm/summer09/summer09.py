import asm.cms
import asm.cms.cmsui
import datetime
import grok
import megrok.pagelet
import time
import zope.interface


class ISummer09(asm.cms.IRetailSkin):
    grok.skin('summer09')


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(ISummer09)
    megrok.pagelet.template('layout.pt')


class LayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(ISummer09)

    def generateCountdown(dummy):
      #request = container.REQUEST
      #RESPONSE =  request.RESPONSE

      # time ( YYYY-MM-DDThh:ss:mmTZD or None), boolean for countdown, string to show
      times = ( ('06.08.2009 12:00', True, "until ASSEMBLY!"),
                ('09.08.2009 18:00', True, "of ASSEMBLY left to enjoy!"),
                (None, False, "ASSEMBLY is over."),)
      format = '%d.%m.%Y %H:%M'

      now = datetime.datetime.now()

      for (limitString, doCountDown, showString) in times:
          limit = None
          if limitString:
              limit = datetime.datetime.strptime(limitString, format)
          if (not limit) or now < limit:
              if doCountDown:
                  diff = (limit - now).seconds
                  countdown = ""
                  units = (('years',31536000),('months',2592000),('days',86400),('hours',3600),('minutes',60),('seconds',1))
                  messageParts = []
                  for (name,length) in units[:-1]:
                      if diff > length:
                          #messageParts.append('<strong id="clock_%s">%s</strong> %s' % (name,int(diff/length),context.translate(name,domain="asm")))
                          messageParts.append('<strong id="clock_%s">%s</strong> %s' % (name,int(diff/length),name))
                          diff = diff%length

                  #message = '<span id="clock" alt="%s">%s %s</span>' % (limit.millis(),', '.join(messageParts), context.translate(showString,domain="asm"))
                  message = '<span id="clock">%s %s</span>' % (', '.join(messageParts), showString)
              else:
                  pass
                  message = "foo"
              return message

      # This should never get returned...
      return "Welcome to Assembly!"


    # A helper class to get access to the static directory in this module from
    # the layout.
    def render(self):
        return ''


class Navtree(asm.cms.cmsui.Navtree):
  grok.layer(ISummer09)
  grok.context(zope.interface.Interface)
