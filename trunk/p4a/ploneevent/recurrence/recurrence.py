import datetime
from dateutil import rrule
from zope import interface
from zope import component
from zope.app.annotation import interfaces as annointerfaces

from p4a.common.dtutils import DT2dt
from p4a.ploneevent.recurrence import interfaces

from Products.ATContentTypes.content.event import ATEvent

from dateable import kalends


class RecurrenceSupport(object):
    """Recurrence support.
    """
    interface.implements(kalends.IRecurrence)
    component.adapts(ATEvent)

    def __init__(self, context):
        self.context = context

    def getRecurrenceRule(self):
        """Returns a dateutil.rrule."""
        if getattr(self.context, 'frequency', -1) is -1:
            return None

        dtstart = DT2dt(self.context.startDate)
        params = dict(
            dtstart=dtstart,
            #wkst=None,
            #byyearday=None,
            #byeaster=None,
            #byweekno=None,
            #byhour=None,
            #byminute=None,
            #bysecond=None,
            #cache=False
        )

        # byweekday
        days = [int(day) for day in self.context.byweek]
        if not days:
            days = [dtstart.weekday()]
        if self.context.frequency == rrule.WEEKLY:
            params['byweekday'] = days
        elif self.context.frequency in (rrule.MONTHLY, rrule.YEARLY) and \
           self.context.repeatday == 'dayofweek':
            if self.context.ordinalweek:
                weekrepeat = [int(week) for week in self.context.ordinalweek]
                days = [rrule.weekdays[d](w) for w in weekrepeat for d in days]
            params['byweekday'] = days

        # bymonthday
        if self.context.frequency in (rrule.MONTHLY, rrule.YEARLY) and \
           self.context.repeatday == 'dayofmonth':
            params['bymonthday'] = dtstart.day

        # bymonth
        months = [int(month) for month in self.context.bymonth]
        if not months:
            months = [dtstart.month]
        if self.context.frequency == rrule.YEARLY:
            params['bymonth'] = months

        # interval
        if self.context.interval:
            params['interval'] = self.context.interval

        # count
        if self.context.ends == 'count' and self.context.count:
            params['count'] = self.context.count

        # until
        if self.context.ends == 'until' and self.context.until:
            until = DT2dt(self.context.until)
            until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
            params['until'] = until

        return rrule.rrule(self.context.frequency, **params)

    def getOccurrenceDays(self, until=None):
        """Days on which the event occurs. Used for indexing."""
        rule = self.getRecurrenceRule()
        if rule is None:
            return []

        if until is None:
            until = datetime.datetime.now() + \
                    datetime.timedelta(365*5)

        if until.tzinfo is None and rule._dtstart.tzinfo is not None:
            until = until.replace(tzinfo=rule._dtstart.tzinfo)

        if until.tzinfo is not None and rule._dtstart.tzinfo is None:
            until = until.replace(tzinfo=None)

        if rule._until is None or rule._until > until:
            rule._until = until

        return [x.date().toordinal() for x in rule][1:]


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
