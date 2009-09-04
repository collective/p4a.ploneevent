from zope.i18n import translate
from Products.Five.browser import BrowserView
from dateable.kalends import IRecurringEvent, IRecurrence
from p4a.common.dtutils import dt2DT
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from p4a.common.dtutils import DT2dt, gettz

from p4a.ploneevent.recurrence.recurrence import RecurrenceSupport

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
        
    def getDatesForOccurrence(self):
        """ Return start and end dates for a specific occurrence
        Pass in the index of the occurence and return start
        and end dates to display in event view """
        return IRecurrence(self.context, None).getOccurrenceDays()[1]

    def isRecurring(self):
        return IRecurringEvent.providedBy(self.context)

    def rrule(self):
        return IRecurrence(self.context, None).getRecurrenceRule()

    def rrule_freq(self):
        rrule = self.rrule()
        if rrule is None:
            return ''
        # D.H. 20090622: Commented out to integrate with lingo string
        #if rrule._interval == 1:
            #text = u"Every ${frequency}"
        #else:
            #text = u"Every ${interval} ${frequency}s"

        #return translate(text, mapping={'interval':rrule._interval, 
                                        #'frequency':FREQ[rrule._freq]})

        # TODO: Re-integrate new code with i18n
        lib = RecurrenceSupport(self.context)
        startDate = DT2dt(self.context.startDate)
        iWeek = lib.getWeekInMonthFromDate(startDate)
        text = lib._buildRecurrenceString(rrule._freq, rrule._interval, 
                                          startDate, iWeek)
        return text

    def rrule_interval(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._interval
        return 0
    
    def rrule_count(self):
        if self.context.ends==False and self.context.count > 1:
            return self.context.count
        else:
            return None
        
    def rrule_end(self):
        rrule = self.rrule()
        if rrule is not None and rrule._until:
            return self.context.toLocalizedTime(dt2DT(rrule._until), long_format=0)
        return ''
        
class OccurrenceView(EventView):
    """ provides methods for returning event occurrence-specific 
        date values. Times will be consistent with original Event obj
        values """
        
    def __init__(self, context, request):        
        self.ordinalstart = int(request.r)
        self.startdate = datetime.fromordinal(self.ordinalstart).replace(tzinfo=gettz())
        #self.startdate = self.startdate.replace() ### replace the hours minutes with correct time
        self.daysduration = 2 #dummy
        self.enddate = self.startdate + timedelta(days=self.daysduration)        
        EventView.__init__(self, context, request)
        
    def same_day(self):
        return False

    def short_start_date(self):
        return self.context.toLocalizedTime(self.startdate.isoformat(), long_format=0)
        
    def long_start_date(self):
        return self.context.toLocalizedTime(self.startdate.isoformat(), long_format=1)

    def short_end_date(self):
        return self.context.toLocalizedTime(self.enddate.isoformat(), long_format=0)
    
    def long_end_date(self):
        return self.context.toLocalizedTime(self.enddate.isoformat(), long_format=1)
        


class RecurrenceView(PloneKSSView):

    @kssaction
    def updateRecurUI(self, frequency=None, interval=None, ends=None, 
                      startDate=None, repeatday=None):
        # build HTML
        content ='Repeats every %s  %s '
        DAYOFWEEK =''
        core = self.getCommandSet('core')

        #check to see if single interval
        try:
            frequency = int(frequency)
        except TypeError:
            frequency = -1
        try:
            interval = int(interval)
        except TypeError:
            interval = ''

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
        
        #hide initially
        
        #commenting out byweekday (widget marked invisible) until working
        #core.setStyle('#archetypes-fieldname-byweekday', name='display', value='none') 
        core.setStyle('#archetypes-fieldname-repeatday', name='display', value='none')
        core.setStyle('#archetypes-fieldname-until', name='display', value='none')
        core.setStyle('#archetypes-fieldname-count', name='display', value='none')
        
        core.setStyle('#archetypes-fieldname-interval', name='display', value=display)
        core.setStyle('#archetypes-fieldname-ends', name='display', value=display)
        
        if frequency == 1: #monthly
            core.setStyle('#archetypes-fieldname-repeatday', name='display', value='block')
            
        elif frequency == 2:  #weekly
            pass
            #commenting out byweekday (widget marked invisible) until working
            #core.replaceInnerHTML('#byweekday_help', 'Repeats on')        
            #core.setStyle('#archetypes-fieldname-byweekday', name='display', value='block') 

        if not ends:
            core.setStyle('#archetypes-fieldname-until', name='display', value='block') 
            core.setStyle('#archetypes-fieldname-count', name='display', value='block')            
                      
        #if ends:
        #    core.setStyle('#archetypes-fieldname-until', name='display', value='none') 
        #    core.setStyle('#archetypes-fieldname-count', name='display', value='none')            
                    
        #if frequency != 1:
        #    core.setStyle('#archetypes-fieldname-repeatday', name='display', value='none')
            
        #if frequency != 1:
        #    core.setStyle('#archetypes-fieldname-byweek', name='display', value='none')
            
        #if frequency == 1:
 
        content = content % (interval, caltext)         
        core.replaceInnerHTML('#interval_help', content)
        
        text = self.getRecurrenceString(core.context, startDate, frequency, 
                                        interval, repeatday)
        core.replaceInnerHTML('#archetypes-fieldname-lingo', text)
    
    def getRecurrenceString(self, event, strStartDate, frequency, interval, 
                            repeatday):
        if frequency == -1:
            return ''
        iInterval = interval
        if interval == '' or interval is None:
            iInterval = 1
        lib = RecurrenceSupport(event)
        dateStart =  DT2dt(DateTime(strStartDate))
        if repeatday == 'dayofweek':
            iWeek = lib.getWeekInMonthFromDate(dateStart)
        else:
            iWeek=-1
        text = lib._buildRecurrenceString(frequency, iInterval, dateStart, iWeek)
        return text


