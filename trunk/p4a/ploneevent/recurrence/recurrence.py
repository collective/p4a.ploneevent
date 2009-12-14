import datetime
import calendar
from dateutil import rrule, tz
from zope import interface
from zope import component
from zope.app.annotation import interfaces as annointerfaces

from persistent.dict import PersistentDict

from p4a.ploneevent.recurrence import interfaces
from p4a.common.descriptors import anno
from p4a.common.dtutils import DT2dt

from Products.ATContentTypes.content.event import ATEvent

from dateable import kalends

#temp import
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY


class RecurrenceSupport(object):
    """Recurrence support"""

    interface.implements(kalends.IRecurrence)
    component.adapts(ATEvent)
    IDX_YEAR = 0
    IDX_MONTH = 1
    IDX_WEEK = 2
    IDX_DAY = 3
    LIST_PREFIX = ['Every', 'Every', 'Every', 'Every']
    LIST_INTERVAL_TYPES = ['year', 'month', 'week', 'day']
    LIST_PREPOSITION_START_DATE = ['on', 'on the', 'on']
    LIST_RANGE = ['','','two','three','four','five','six','seven','eight','nine']
    LIST_ORDINALS = ['',
                     'st','nd','rd','th','th','th','th','th','th','th',
                     'th','th','th','th','th','th','th','th','th','th',
                     'st','nd','rd','th','th','th','th','th','th','th',
                     'st']

    def __init__(self, context):
        self.context = context

    def getDayofWeek(self):

        dtstart = DT2dt(self.context.startDate)
        
        if getattr(self.context,'byweekday',None) and \
          self.context.frequency == 3:
            return tuple([int(day) for day in self.context.byweekday])       
        if self.context.frequency != 1:
            return None
        if self.context.repeatday[0] == 'dayofmonth':
            return None
        if getattr(self.context,'byweekday',None) and \
          len(self.context.byweekday) == 0 or self.context.frequency == 1:
            return tuple([dtstart.weekday()])
        
    def getWeekNumber(self):
        """returns the number of the week for specific date"""
        dtstart = DT2dt(self.context.startDate)
        #need to test if monthly otherwise return -1 ?
        if self.context.repeatday[0] == 'dayofmonth':
            return -1
        if self.context.frequency != 1:
            return -1
        return self.getWeekInMonthFromDate(dtstart)
            
    def getWeekInMonthFromDate(self,dtTest):
        """returns the number of the week for a given date"""
        iWeekIndex = 1
        weeks = calendar.monthcalendar(dtTest.year,dtTest.month)
        for week in weeks:
            if week.count(dtTest.day):
                iDayOfWeek = week.index(dtTest.day)
                iWeekIndex = weeks.index(week) + 1
                for week in weeks:
                    if not week[iDayOfWeek]:
                        iWeekIndex -= 1
        return iWeekIndex
        
    def getRecurrenceRule(self):
        """Returns a dateutil.rrule"""
        if getattr(self.context, 'frequency', -1) is -1:
            return None
        
        dtstart = DT2dt(self.context.startDate)       
        
        #if ends ('repeat forever') is true, this overrides any values
        #in until and count   
        if self.context.until is not None and not self.context.ends:
            until = DT2dt(self.context.until)
            until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            until = None
            
        if self.context.count is not None and not self.context.ends:
            count = self.context.count
        else:
            count = None    
            
        rule = rrule.rrule(self.context.frequency,
                           dtstart=dtstart,
                           interval=self.context.interval,
                           #wkst=None, 
                           count=count, 
                           until=until, 
                           bysetpos= self.getWeekNumber(),
                           #bymonth=None, bymonthday=None, byyearday=None, byeaster=None,
                           #byweekno=None, 
                           #bymonthday= dtstart.day,
                           byweekday= self.getDayofWeek(),
                           #byhour=None, byminute=None, bysecond=None,
                           #cache=False
                       )
        return rule

    def getOccurrenceDays(self, until=None):
        """Days on which the event occurs. Used for indexing"""
        # XXX Handle when there is no occurrence.
        rule = self.getRecurrenceRule()
        if rule is None:
            return []
        if until is None:
            if hasattr(self.context, 'until') and self.context.until:
                until = DT2dt(self.context.until)
                until = until.replace(hour=23, minute=59, second=59, 
                                      microsecond=999999)                
            else:
                until = datetime.datetime.now() + \
                        datetime.timedelta(365*5)

        if until.tzinfo is None and rule._dtstart.tzinfo is not None:
            until = until.replace(tzinfo=rule._dtstart.tzinfo)
            
        if until.tzinfo is not None and rule._dtstart.tzinfo is None:
            until = until.replace(tzinfo=None)
                            
        if rule._until is None or rule._until > until:
            rule._until = until
        
        occurrenceDays = [x.date().toordinal() for x in rule][1:]  
        
        # remove from list ordinal dates stored as recurrence exceptions
        # probably a more efficient way of doing this.
        if self.context.exceptions:
            filteredDays = []
            for d in occurrenceDays:
                if str(d) not in self.context.exceptions:
                    filteredDays.append(d)
            return filteredDays        
        
        return occurrenceDays
            
        

    def _buildRecurrenceString(self, iFrequency, iInterval, dateStart, 
                               iWeek=-1):
        """ PRE: iFrequency is an index where 0 is year, 1 is month, 2 is week, 
        and 3 is day, iInterval is any non-zero natural number, and dateStart 
        is a DateTime object indicating the begin date of the recurring event. 
        iWeek is the zero-based index of the week in a monthly recurrence like
        '2nd Tuesday'; do not pass iWeek if describing a monthly recurrence 
        like '11th day'.
        POST: Returns a string describing the recurring event using plain 
        English.
        """
        cls = RecurrenceSupport
        try: #TODO: figure out why in tests we need the property and when running
             #the site we need the method.  Should have to do with datetime vs.
             #DateTime, I think
            iDay = dateStart.day()
        except:
            iDay = dateStart.day    
        strDayOrd = "%d%s" % (iDay, cls.LIST_ORDINALS[iDay])
        strWeekday = dateStart.strftime('%A')
        listParts = []
        listParts.append(cls.LIST_PREFIX[iFrequency])         # Every
        if iInterval > 1:
            if iInterval < 10:
                listParts.append(cls.LIST_RANGE[iInterval])   # three
            else:
                listParts.append('%d' % iInterval)
        strTmp = cls.LIST_INTERVAL_TYPES[iFrequency]
        if iInterval > 1:
            strTmp += 's'                                     # weeks
        listParts.append(strTmp)
        try:
            listParts.append(cls.LIST_PREPOSITION_START_DATE[iFrequency])
        except IndexError:
            pass
        if iFrequency == cls.IDX_YEAR:
            listParts.append(dateStart.strftime('%B %%s') % strDayOrd)
        elif iFrequency == cls.IDX_WEEK:
            listParts.append(strWeekday)
        elif iFrequency == cls.IDX_MONTH:
            if iWeek == -1:
                strTmp = "%s day" % strDayOrd
            else:
                strWeek = "%d%s" % (iWeek, cls.LIST_ORDINALS[iWeek])
                strTmp = "%s %s" % (strWeek, strWeekday)
            listParts.append(strTmp)
        return ' '.join(listParts)


class EventRecurrenceConfig(object):
    """An IRecurrenceConfig adapter for events.
    """
    
    interface.implements(interfaces.IRecurrenceConfig)
    component.adapts(ATEvent)

    def __init__(self, context):
        self.context = context

    def __get_is_recurring(self):
        return kalends.IRecurringEvent.providedBy(self.context) and \
               annointerfaces.IAttributeAnnotatable.providedBy(self.context)
    def __set_is_recurring(self, activated):
        ifaces = interface.directlyProvidedBy(self.context)
        if activated:
            if not kalends.IRecurringEvent.providedBy(self.context):
                ifaces += kalends.IRecurringEvent
            if not annointerfaces.IAttributeAnnotatable.providedBy(self.context):
                ifaces += annointerfaces.IAttributeAnnotatable
            if getattr(self.context, 'layout', None) is not None:
                self.context.layout = 'month.html'
        else:
            if kalends.IRecurringEvent in ifaces:
                ifaces -= kalends.IRecurringEvent
            if getattr(self.context, 'layout', None) is not None:
                delattr(self.context, 'layout')
        interface.directlyProvides(self.context, ifaces)

    is_recurring = property(__get_is_recurring,
                            __set_is_recurring)
