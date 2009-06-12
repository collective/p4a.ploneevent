from zope import component, interface
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

from dateable.kalends import IRecurringEvent
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from p4a.ploneevent.interfaces import IEventSchemaExtension

from Products.Archetypes import atapi
from Products.Archetypes.utils import OrderedDict
from Products.ATContentTypes.content.event import ATEvent


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

        IntegerField(
            name='frequency',
            schemata='recurrence',
            required=True,
            vocabulary=[
                (-1, u'Does not repeat'),
                (YEARLY, u'Yearly'),
                (MONTHLY, u'Monthly'),
                (WEEKLY, u'Weekly'),
                (DAILY, u'Daily'),
            ],
            default=-1,
            widget=atapi.SelectionWidget(
                label=u'Repeats',
            ),
        ),

        IntegerField(
            name='interval',
            schemata='recurrence',
            required=True,
            default=1,
            widget=atapi.IntegerWidget(
                label=u'Repeats every',
                description=u'Repeats every day/week/month/year.',
            ),
        ),

        LinesField(
            name='byweek',
            schemata='recurrence',
            multiValued=True,
            vocabulary=[
                (u'0', u'Monday'),
                (u'1', u'Tuesday'),
                (u'2', u'Wednesday'),
                (u'3', u'Thursday'),
                (u'4', u'Friday'),
                (u'5', u'Saturday'),
                (u'6', u'Sunday'),
            ],
            widget=atapi.MultiSelectionWidget(
                label=u'Day of the week',
                description=u'Days of the week.',
                format='checkbox',
            ),
        ),

        LinesField(
            name='repeatday',
            schemata="recurrence",
            default='on',
            vocabulary=[
                (u'dayofmonth', u'day of the month'),
                (u'dayofweek', u'day of the week'),
            ],
            widget=atapi.SelectionWidget(
                label=u'Repeats by',
                description=u'Select day of week or date.',
                format='radio',
            ),
        ),

        BooleanField(
            name='ends',
            schemata='recurrence',
            default='on',
            widget=atapi.BooleanWidget(
                label=u'Repeat Forever',
                description=u'Event repeats indefinitely.',
            ),
        ),

        IntegerField(
            name='count',
            schemata='recurrence',
            widget=atapi.IntegerWidget(
                label=u'Count',
                description=u'Maxinum number of times the event repeats.',
            ),
        ),

        DateTimeField(
            name='until',
            schemata='recurrence',
            widget=atapi.CalendarWidget(
                label=u'Repeats Until',
                description=u'Event repeats until this date.',
                show_hm=True,
            ),
        ),

    ]

    def __init__(self, extender, context):
        pass

    def getFields(self):
        return self.fields

    def getOrders(self):
        return [(10, 'recurrence')]
