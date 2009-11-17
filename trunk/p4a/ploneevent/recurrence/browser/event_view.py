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

from zExceptions import NotFound

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


    def __init__(self,context,request): 
        """ return 404 error if there is no occurrence on the date
            passed in to request as ordinal
        """ 
        BrowserView.__init__(self,context,request)           
        if self.request.has_key('r'):
            dtOrd = int(self.request['r'])
            if not self.isRecurring() or \
             dtOrd not in IRecurrence(self.context, None).getOccurrenceDays():
                raise NotFound(context, request)


    # XXX TODO: Would be nicer to use a custom __bobo_traverse__ method
    # a la /image/image_mini to be able to use urls like /my-event/733681
    # or better yet /my-event/2009/10/01,  
    # rather than /my-event/?r=733681       
    def start(self):
        date = DateTime(self.context.start())
        if self.isRecurring() and self.request.has_key('r'):
            current = int(self.request['r'])
            date = datetime.fromordinal(current).replace(tzinfo=gettz())
            #since we are passing ordinal date equal to 12:00am of that day,
            #must add hours and minutes from original event
            date = date + \
              timedelta(hours=self.context.start().hour(),\
                        minutes=self.context.start().minute())
            date = dt2DT(date)  
            
        return date

    def end(self):
        offset = self.context.end() - self.context.start()
        #XXX TODO otherwise returning 1 minute before 
        # appropriate end time, but could be done more elegantly
        return self.start() + offset + 0.000001
    
    def same_day(self):
        return self.start().Date() == self.end().Date()

    def short_start_date(self):
        return self.context.toLocalizedTime(self.start(), long_format=0)
        
    def long_start_date(self):
        return self.context.toLocalizedTime(self.start(), long_format=1)
    
    def start_time(self):
        return self.context.start().strftime(self.time_format())

    def short_end_date(self):
        return self.context.toLocalizedTime(self.end(), long_format=0)
    
    def long_end_date(self):
        return self.context.toLocalizedTime(self.end(), long_format=1)

    def end_time(self):
        return self.end().strftime(self.time_format())

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


