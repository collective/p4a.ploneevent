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

        StringField(
            name='repeatday',
            schemata='recurrence',
            vocabulary=[
                (u'dayofmonth', u'day of the month'),
                (u'dayofweek', u'day of the week'),
            ],
            default='dayofmonth',
            widget=atapi.SelectionWidget(
                label=u'Repeats by',
                description=u'Repeats on a specific day of the '
                            u'month or in a day of the week.',
                format='radio',
            ),
        ),

        IntegerField(
            name='byday',
            schemata='recurrence',
            widget=atapi.IntegerWidget(
                label=u'Day',
                description=u'Repeats on this day.',
            ),
        ),

        LinesField(
            name='ordinalweek',
            schemata='recurrence',
            multiValued=True,
            vocabulary=[
                (u'1', u'first'),
                (u'2', u'second'),
                (u'3', u'third'),
                (u'4', u'fourth'),
                (u'-1', u'last'),
            ],
            widget=atapi.MultiSelectionWidget(
                label=u'Week',
                description=u'Repeats on specific week(s).',
                format='checkbox',
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
                label=u'Week Day',
                description=u'Repeat in the selected day(s) of the week.',
                format='checkbox',
            ),
        ),

        LinesField(
            name='bymonth',
            schemata='recurrence',
            multiValued=True,
            vocabulary=[
                (u'1', u'January'),
                (u'2', u'February'),
                (u'3', u'March'),
                (u'4', u'April'),
                (u'5', u'May'),
                (u'6', u'June'),
                (u'7', u'July'),
                (u'8', u'August'),
                (u'9', u'September'),
                (u'10', u'October'),
                (u'11', u'November'),
                (u'12', u'December'),
            ],
            widget=atapi.MultiSelectionWidget(
                label=u'Month',
                description=u'Repeat in the selected month(s) of the year.',
                format='checkbox',
            ),
        ),

        IntegerField(
            name='interval',
            schemata='recurrence',
            required=True,
            default=1,
            widget=atapi.IntegerWidget(
                label=u'Every',
                description=u'Repeats every day/week/month/year.',
            ),
        ),

        StringField(
            name='ends',
            schemata='recurrence',
            default='0',
            vocabulary=[
                (u'0', u'No end date'),
                (u'1', u'End after a number of occurrences'),
                (u'2', u'End on a specific date'),
            ],
            widget=atapi.SelectionWidget(
                label=u'Range of recurrence',
            ),
        ),

        IntegerField(
            name='count',
            schemata='recurrence',
            widget=atapi.IntegerWidget(
                label=u'Count',
                description=u'Event repeats this number of times.',
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
