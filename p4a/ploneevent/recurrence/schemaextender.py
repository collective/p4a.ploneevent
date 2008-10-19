# Trying to use archetypes.schemaextender
from zope import component, interface
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.Archetypes.utils import OrderedDict
from Products.ATContentTypes.content.event import ATEvent
from dateable.kalends import IRecurringEvent
from p4a.ploneevent.interfaces import IEventSchemaExtension
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY


class TextField(ExtensionField, atapi.TextField):
     pass

class DateTimeField(ExtensionField, atapi.DateTimeField):
     pass

class IntegerField(ExtensionField, atapi.IntegerField):
     pass

class StringField(ExtensionField, atapi.StringField):
     pass

class RecurrenceExtension(object):
     component.adapts(IOrderableSchemaExtender, IRecurringEvent)
     interface.implements(IEventSchemaExtension)

     fields = [
          IntegerField('frequency',
               schemata="recurrence",
               required=True,
               vocabulary={-1: u'Does not repeat',
                           YEARLY: u'Yearly',
                           MONTHLY: u'Monthly',
                           WEEKLY: u'Weekly',
                           DAILY: u'Daily',
                           }.items(),
               default=-1,
               widget=atapi.SelectionWidget(label=u'Repeats')
               ),
          IntegerField('interval',
               schemata="recurrence",
               required=True,
               default=1,
               widget=atapi.IntegerWidget(label=u'Repeats every',
                    description=u"Repeats every day/week/month/year.")
               ),
          DateTimeField('until',
               schemata="recurrence",
               widget=atapi.CalendarWidget(label=u'Range',
                    description=u"Event repeats until this date.",
                    show_hm=True)
               ),
          IntegerField('count',
                schemata="recurrence",
                widget=atapi.IntegerWidget(label=u'Count',description=u'Maxinum number of times the event repeats ',)
                ),
          ]

     def __init__(self, extender, context):
          pass

     def getFields(self):
          return self.fields
     
     def getOrders(self):
          return [(10, 'recurrence')]
