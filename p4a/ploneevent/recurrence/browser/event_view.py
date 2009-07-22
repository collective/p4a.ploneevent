from zope.i18n import translate
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from dateable.kalends import IRecurringEvent, IRecurrence
from p4a.common.dtutils import dt2DT
from kss.core import KSSView, kssaction
from datetime import datetime
from p4a.ploneevent import p4a_messagefactory as _

CALVOCAB = {  -1: (u'', u'', _(u'Does not repeat')),
               0: (_(u'Year'), _(u'Years'), _(u'Yearly')),
               1: (_(u'Month'), _(u'Months'), _(u'Monthly')),
               2: (_(u'Week'), _(u'Weeks'), _(u'Weekly')),
               3: (_(u'Day'), _(u'Days'), _(u'Daily')),
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

    @property
    def language(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state")
        
        return portal_state.language()
        
    def rrule_freq(self):
        rrule = self.rrule()

        if rrule is None:
            return u''
        elif rrule._freq == -1:
            caltext = CALVOCAB[rrule._freq][0]
        elif rrule._interval > 1:
            caltext = CALVOCAB[rrule._freq][1]
        elif rrule._interval == 0:
            caltext = _('day/week/month/year')
        else: 
            caltext = CALVOCAB[rrule._freq][2]
        
        translated_caltext = translate(caltext, target_language=self.language)

        if rrule._interval > 1:
            content = _(u'Repeats every ${interval} ${frequency}.', 
                        mapping=dict(interval=rrule._interval, 
                                     frequency=translated_caltext))
        else:
            # some languages need another language string to translate singular
            # and plural message strings differently. 
            content = _(u'Repeats ${frequency}.', 
                        mapping=dict(frequency=translated_caltext))

        return translate(content, target_language=self.language)
        
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
    
    @property
    def language(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state")
        
        return portal_state.language()

    @kssaction
    def updateRecurUI(self, frequency, interval):
        core = self.getCommandSet('core')
        
        # skip this if frequency or interval typecast throws an exception.
        # this happens if no value is entered into the field.
        try:
            frequency = int(frequency)
            interval  = int(interval)
        except ValueError:
            return 
        
        if frequency == -1:
            caltext = CALVOCAB[frequency][0]
            display = 'none'
        elif interval > 1:
            caltext = CALVOCAB[frequency][1]
            display = 'block'
        elif interval == 0:
            caltext = _('day/week/month/year')
            display = 'block'
        else: 
            caltext = CALVOCAB[frequency][2]
            display = 'block'
        
        translated_caltext = translate(caltext, target_language=self.language)
        
        core.setStyle('#archetypes-fieldname-interval', name='display', value=display)
        core.setStyle('#archetypes-fieldname-until', name='display', value=display)
        core.setStyle('#archetypes-fieldname-count', name='display', value=display)
        
        if interval > 1:
            content = _(u'Repeats every ${interval} ${frequency}.', 
                        mapping=dict(interval=interval, 
                                     frequency=translated_caltext))
        else:
            # some languages need another language string to translate singular
            # and plural message strings differently. 
            content = _(u'Repeats ${frequency}.', 
                        mapping=dict(frequency=translated_caltext))
        
        core.replaceInnerHTML('#interval_help', 
                              translate(content, target_language=self.language))
        