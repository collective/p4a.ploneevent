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
        iDay = dateStart.day()
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
