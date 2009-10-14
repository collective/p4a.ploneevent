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

class LinesField(ExtensionField, atapi.LinesField):
     pass
      
class BooleanField(ExtensionField, atapi.BooleanField):
     pass

class RecurrenceExtension(object):
     component.adapts(IOrderableSchemaExtender, IRecurringEvent)
     interface.implements(IEventSchemaExtension)
     
     fields = [
          StringField('lingo',
               schemata='default',
               widget=atapi.LabelWidget(label=u'')
               ),
          IntegerField('frequency',
               schemata="default",
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
               schemata="default",
               required=True,
               default=1,
               widget=atapi.IntegerWidget(label=u'Repeats every',
                    description=u"Repeats every day/week/month/year.")
               ),
          LinesField('byweekday',
               schemata="default",
               multiValued=True,               
               vocabulary=[(u'0', u'Monday'),
                           (u'1', u'Tuesday'),
                           (u'2', u'Wednesday'),
                           (u'3', u'Thursday'),
                           (u'4', u'Friday'),
                           (u'5', u'Saturday'), 
                           (u'6', u'Sunday'), 
                           ], 

               widget=atapi.MultiSelectionWidget(label=u'Day of the week',
               format="checkbox",
               visible={'edit': 'invisible', 'view': 'invisible'},
               description=u"Days of the week")
               ),
          LinesField('repeatday',
             schemata="default",
             default='dayofmonth',
            vocabulary=[(u'dayofmonth', u'Day of the month'),
                        (u'dayofweek', u'Day of the week'), 
                        ],
             widget=atapi.SelectionWidget(label=u'Repeats by ',
                  format = 'radio',
                  description=u"Repeat by day of the month or weekday",
                  )
             ),                 
          BooleanField('ends',
                  schemata="default",
                  default='on',
                  widget=atapi.BooleanWidget(label=u'Repeat Forever',
                       description=u"Event repeats indefinitely.",
                       )
                  ),                    
          DateTimeField('until',
               schemata="default",
               widget=atapi.CalendarWidget(label=u'Repeats Until',
                    description=u"Event repeats until this date.",
                    show_hm=False)
               ),
          IntegerField('count',
                schemata="default",
                widget=atapi.IntegerWidget(label=u'Repeats For',
                    description=u'Maximum number of times the event repeats ',)
                ),
          LinesField('exceptions',
                schemata="default",
                multiValued=True,
                widget=atapi.LinesWidget(label=u'Recurrence Exceptions',
                    description=u'Ordinal dates of event exceptions. \
                      Occurrences will not be displayed for these dates.',),
                    modes=('edit',),
                    visible={'view': 'hidden', 'edit': 'visible' } ,                    
                ),

          ]

     def __init__(self, extender, context):
          pass

     def getFields(self):
          return self.fields
     
     def getOrders(self, original):
          default = original['default']
          idx = default.index('endDate') + 1
          newfields = []
          for field in self.fields:
               default.remove(field.__name__)
               default.insert(idx,field.__name__)
               idx=idx+1
          return [(0,'default')]
          #return [(10,'recurrence')]