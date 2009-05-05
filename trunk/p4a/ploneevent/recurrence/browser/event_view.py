from zope.i18n import translate
from Products.Five.browser import BrowserView
from dateable.kalends import IRecurringEvent, IRecurrence
from p4a.common.dtutils import dt2DT
from kss.core import KSSView, kssaction
from datetime import datetime

FREQ = {0: 'year',
        1: 'month',
        2: 'week',
        3: 'day',
        4: 'hour',
        5: 'minute',
        6: 'second',
    }
    
    
CALVOCAB = {   0: (u'Year', u'Years'),
               1: (u'Month', u'Months'),
               2: (u'Week', u'Weeks'),
               3: (u'Day', u'Days'),
                }

class EventView(BrowserView):
    
    def same_day(self):
        return self.context.start().Date() == self.context.end().Date()

    def short_start_date(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=0)
        
    def long_start_date(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=1)
    
    def start_time(self):
        return self.context.start().strftime(self.time_format())

    def short_end_date(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=0)
    
    def long_end_date(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=1)

    def end_time(self):
        return self.context.end().strftime(self.time_format())

    def datetime_format(self):
        site_properties = self.context.portal_properties.site_properties
        return site_properties.getProperty('localLongTimeFormat')

    def date_format(self):
        site_properties = self.context.portal_properties.site_properties
        return site_properties.getProperty('localTimeFormat')
    
    def time_format(self):
        datetime_format = self.datetime_format()
        if '%p' in datetime_format:
            # Using AM/PM:
            return ' '.join(datetime_format.split(' ')[-2:])
        # 24 H format
        return datetime_format.split(' ')[-1]

    def isRecurring(self):
        return IRecurringEvent.providedBy(self.context)

    def rrule(self):
        return IRecurrence(self.context, None).getRecurrenceRule()

    def rrule_freq(self):
        rrule = self.rrule()
        if rrule is None:
            return ''
        if rrule._interval == 1:
            text = u"Every ${frequency}"
        else:
            text = u"Every ${interval} ${frequency}s"

        return translate(text, mapping={'interval':rrule._interval, 
                                        'frequency':FREQ[rrule._freq]})
    def rrule_interval(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._interval
        return 0
        
    def rrule_end(self):
        rrule = self.rrule()
        if rrule is not None and rrule._until:
            return self.context.toLocalizedTime(dt2DT(rrule._until), long_format=0)
        return ''


class RecurrenceView(KSSView):

    @kssaction
    def updateRecurUI(self, frequency,interval):
        # build HTML
        content ='Repeats every %s  %s '
        core = self.getCommandSet('core')

        #check to see if single interval
        frequency = int(frequency)
        interval  = int(interval)
        if frequency == -1:
            caltext = 'day/week/month/year.'
            interval = ''
            display = 'none'
        elif interval > 1:
            caltext = CALVOCAB[frequency][1]
            display = 'block'
        elif interval == 0:
            caltext = 'day/week/month/year.'
            interval = ''
            display = 'block'
        else: 
            caltext = CALVOCAB[frequency][0]
            interval = '' 
            display = 'block'
         
        core.setStyle('#archetypes-fieldname-interval', name='display', value=display)
        core.setStyle('#archetypes-fieldname-until', name='display', value=display)
        core.setStyle('#archetypes-fieldname-count', name='display', value=display)
        content = content % (interval, caltext)         
        core.replaceInnerHTML('#interval_help', content)