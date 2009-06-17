from zope import schema
from zope import interface


class IRecurrenceConfig(interface.Interface):
    """Configuration information for an event.
    """

    is_recurring = schema.Bool(
        title=u'Recurring event',
        description=u'This event recurs'
        )

# BBB
from dateable.kalends import IRecurringEvent
