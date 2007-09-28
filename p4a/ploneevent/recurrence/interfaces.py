from zope import interface
from zope import schema

from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY

class IRecurrenceConfig(interface.Interface):
    """Configuration information for an event.
    """
    
    is_recurring = schema.Bool(
        title=u'Recurring event',
        description=u'This event recurs'
        )


class IRecurringEvent(interface.Interface):    
    """Marks the event as recurring"""


class IRecurrenceSupport(interface.Interface):    
    """This interface provides the external API for recurrence"""

    def getRecurrenceRule():
        """Returns a dateutil.rrule"""

    def getOccurrenceDays():
        """Days on which the event occurs. Used for indexing"""

    # Dateutil.rrule also accepts hourly, minutely and secondly,
    # but that's silly in a calendar.
    frequency = schema.Choice(title=u'Recurrence frequency',
        vocabulary=schema.vocabulary.SimpleVocabulary.fromDictionary(
            {YEARLY: u'Yearly',
             MONTHLY: u'Monthly',
             WEEKLY: u'Weekly',
             DAILY: u'Daily',
             }),
        required=True)
    
    until = schema.Date(title=u'Recur until', required=False, default=None)
    
    interval = schema.Int(title=u'Interval', default=1)

    count = schema.Int(title=u'Count', required=False, default=None)

