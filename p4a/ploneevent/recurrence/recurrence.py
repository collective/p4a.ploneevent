import datetime
from zope import interface
from zope import component
from dateable import kalends
from p4a.ploneevent.recurrence import interfaces
from zope.app.annotation import interfaces as annointerfaces
from Products.ATContentTypes.content.event import ATEvent


class RecurrenceSupport(object):
    """Recurrence support.
    """
    interface.implements(kalends.IRecurrence)
    component.adapts(ATEvent)

    def __init__(self, context):
        self.context = context

    def getRecurrenceRule(self):
        """Returns the recurrence rule."""
        recurrence = getattr(self.context, 'recurrence', None)
        if not recurrence or not recurrence.enabled:
            return None
        return recurrence.getRecurrenceRule()

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
    """An IRecurrenceConfig adapter for events."""
    interface.implements(interfaces.IRecurrenceConfig)
    component.adapts(ATEvent)

    def __init__(self, context):
        self.context = context

    @apply
    def is_recurring():
        def get(self):
            return kalends.IRecurringEvent.providedBy(self.context) and \
                   annointerfaces.IAttributeAnnotatable.providedBy(self.context)
        def set(self, activated):
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
