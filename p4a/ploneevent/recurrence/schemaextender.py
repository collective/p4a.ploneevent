from dateutil import rrule
from zope import component, interface
from dateable.kalends import IRecurringEvent

from Products.Archetypes import atapi
from archetypes.recurringdate import field
from archetypes.recurringdate import RecurringDateWidget
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

from p4a.ploneevent import PloneEventMessageFactory as _
from p4a.ploneevent.interfaces import IEventSchemaExtension


class RecurringDateField(ExtensionField, field.RecurringDateField):
    pass


class RecurrenceExtension(object):
    component.adapts(IOrderableSchemaExtender, IRecurringEvent)
    interface.implements(IEventSchemaExtension)

    fields = [

        RecurringDateField(
            name='recurrence',
            schemata='recurrence',
            widget=RecurringDateWidget(),
        ),

    ]

    def __init__(self, extender, context):
        pass

    def getFields(self):
        return self.fields

    def getOrders(self):
        return [(10, 'recurrence')]
