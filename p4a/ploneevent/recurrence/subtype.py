from zope import interface
from p4a.ploneevent.recurrence import interfaces
from p4a.subtyper.interfaces import IPortalTypedDescriptor


class RecurringEventDescriptor(object):
    interface.implements(IPortalTypedDescriptor)

    title = u'Recurring Event'
    description = u'Make the event recur'
    type_interface = interfaces.IRecurringEvent
    for_portal_type = 'Event'

