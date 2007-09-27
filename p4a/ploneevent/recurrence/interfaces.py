from zope import interface
from zope import schema

from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY

class IRecurrenceSupport(interface.Interface):    
    """This interface provides the external API for recurrence"""

    def getRecurrenceRule():
        """Returns a dateutil.rrule"""

    def getOccurrenceDays():
        """Days on which the event occurs. Used for indexing"""

    # Dateutil.rrule also accepts hourly, minutely and secondly,
    # but that's silly in a calendar.
    recurrence_frequency = schema.Choice(title=u'Recurrence frequency',
                                    values=[(YEARLY, u'Yearly'),
                                            (MONTHLY, u'Monthly'),
                                            (WEEKLY, u'Weekly'),
                                            (DAILY, u'Daily'),
                                            ],
                                    required=True,
                                    )
    #description = schema.Text(title=u'Description',
                              #required=False,
                              #readonly=True)
    #start = schema.Datetime(title=u'Start Time',
                            #required=True,
                            #readonly=True)
    #end = schema.Datetime(title=u'End Time',
                          #required=False,
                          #readonly=True)
    #location = schema.TextLine(title=u'Location',
                               #required=False,
                               #readonly=True)
    #local_url = schema.TextLine(title=u'URL',
                                #required=True,
                                #readonly=True)
    #type = schema.TextLine(title=u'Type',
                           #required=True,
                           #readonly=False)
    #timezone = schema.TextLine(title=u'Timezone',
                               #required=True,
                               #readonly=True)


class IRecurringEvent(interface.Interface):    
    """Marks the event as recurring"""


class IRecurrenceConfig(interface.Interface):
    """Configuration information for an event.
    """
    
    is_recurring = schema.Bool(
        title=u'Recurring event',
        description=u'This event recurs'
        )


#class IRecurrenceSchema(interface.Interface):
    #"""The schema for a recurrence rule"""
        
    ## Dateutil.rrule also accepts hourly, minutely and secondly,
    ## but that's silly in a calendar.
    #recurrence_frequency = schema.Choice(title=u'Recurrence frequency',
                                    #values=[(YEARLY, u'Yearly'),
                                            #(MONTHLY, u'Monthly'),
                                            #(WEEKLY, u'Weekly'),
                                            #(DAILY, u'Daily'),
                                            #],
                                    #required=True,
                                    #)
    #description = schema.Text(title=u'Description',
                              #required=False,
                              #readonly=True)
    #start = schema.Datetime(title=u'Start Time',
                            #required=True,
                            #readonly=True)
    #end = schema.Datetime(title=u'End Time',
                          #required=False,
                          #readonly=True)
    #location = schema.TextLine(title=u'Location',
                               #required=False,
                               #readonly=True)
    #local_url = schema.TextLine(title=u'URL',
                                #required=True,
                                #readonly=True)
    #type = schema.TextLine(title=u'Type',
                           #required=True,
                           #readonly=False)
    #timezone = schema.TextLine(title=u'Timezone',
                               #required=True,
                               #readonly=True)
