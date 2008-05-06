from zope.i18n import translate
from Products.Five.browser import BrowserView
from dateable.kalends import IRecurringEvent, IRecurrence
from p4a.common.dtutils import dt2DT

FREQ = {0: 'year',
        1: 'month',
        2: 'week',
        3: 'day',
        4: 'hour',
        5: 'minute',
        6: 'second',
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
        return IRecurringEvent.isImplementedBy(self.context)

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
        