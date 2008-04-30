import datetime

from dateutil import rrule, tz
from zope import interface
from zope import component
from zope.app.annotation import interfaces as annointerfaces

from persistent.dict import PersistentDict

from p4a.ploneevent.recurrence import interfaces
from p4a.calendar import interfaces as calendarinterfaces
from p4a.common.descriptors import anno

from Products.ATContentTypes.content.event import ATEvent

def DT2dt(date, tznaive=False):
    # XXX Test.
    s, ms = divmod(date.second(), 1)
    if tznaive:
        _tz = None
    else:
        _tz = tz.tzoffset(date.timezone(), date.tzoffset())
    dt = datetime.datetime(date.year(), date.month(), date.day(), date.hour(), 
                           date.minute(), int(s), int(ms*1000000), _tz)
    return dt


ANNO_KEY = 'p4a.ploneevent.recurrence'
IIR = interfaces.IRecurrenceSupport

from zope.app.annotation.interfaces import IAnnotatable

class RecurrenceSupport(object):
    """Recurrence support"""

    interface.implements(interfaces.IRecurrenceSupport)
    component.adapts(ATEvent)

    def __init__(self, context):
        self.context = context

    def getRecurrenceRule(self):
        """Returns a dateutil.rrule"""
        if getattr(self.context, 'frequency', None) is None:
            return None
        
        dtstart = DT2dt(self.context.startDate, tznaive=True)
        if self.context.until is not None:
            until = DT2dt(self.context.until, tznaive=True)
            until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            until = None
        # Make it end at the end of the day:

        rule = rrule.rrule(self.context.frequency,
                           dtstart=dtstart,
                           interval=self.context.interval,
                           #wkst=None, 
                           count=self.context.count, 
                           until=until, 
                           #bysetpos=None,
                           #bymonth=None, bymonthday=None, byyearday=None, byeaster=None,
                           #byweekno=None, byweekday=None,
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
            until = datetime.datetime.now() + \
                    datetime.timedelta(365*5)

        if rule._until is not None:
            # Make sure they are not one tznaive and one tzaware object:
            if (until.tzinfo is None and rule._until.tzinfo is not None or
                until.tzinfo is not None and rule._until.tzinfo is None):
                until.replace(tzinfo=None)
            
        if rule._until is None or rule._until > until:
            rule._until = until
        
        return [x.date().toordinal() for x in rule][1:]


class EventRecurrenceConfig(object):
    """An IRecurrenceConfig adapter for events.
    """
    
    interface.implements(interfaces.IRecurrenceConfig)
    component.adapts(calendarinterfaces.IEvent)

    def __init__(self, context):
        self.context = context

    def __get_is_recurring(self):
        return interfaces.IRecurringEvent.providedBy(self.context) and \
               annointerfaces.IAttributeAnnotatable.providedBy(self.context)
    def __set_is_recurring(self, activated):
        ifaces = interface.directlyProvidedBy(self.context)
        if activated:
            if not interfaces.IRecurringEvent.providedBy(self.context):
                ifaces += interfaces.IRecurringEvent
            if not annointerfaces.IAttributeAnnotatable.providedBy(self.context):
                ifaces += annointerfaces.IAttributeAnnotatable
            if getattr(self.context, 'layout', None) is not None:
                self.context.layout = 'month.html'
        else:
            if interfaces.IRecurringEvent in ifaces:
                ifaces -= interfaces.IRecurringEvent
            if getattr(self.context, 'layout', None) is not None:
                delattr(self.context, 'layout')
        interface.directlyProvides(self.context, ifaces)

    is_recurring = property(__get_is_recurring,
                            __set_is_recurring)
