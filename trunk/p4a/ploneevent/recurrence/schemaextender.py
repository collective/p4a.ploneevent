from dateutil import rrule
from dateable.kalends import IRecurringEvent

from zope import component, interface
from Products.Archetypes import atapi
from p4a.ploneevent.interfaces import IEventSchemaExtension
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender


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
        
        IntegerField(
            name='frequency',
            schemata='default',
            required=True,
            vocabulary=[
                (-1, u'Does not repeat'),
                (rrule.YEARLY, u'Yearly'),
                (rrule.MONTHLY, u'Monthly'),
                (rrule.WEEKLY, u'Weekly'),
                (rrule.DAILY, u'Daily'),
            ],
            default=-1,
            widget=atapi.SelectionWidget(
                label=u'Repeats',
            ),
        ),

        StringField(
            name='repeatday',
            schemata='default',
            vocabulary=[
                (u'dayofmonth', u'Day of the month'),
                (u'dayofweek', u'Day of the week'),
            ],
            default='dayofmonth',
            widget=atapi.SelectionWidget(
                label=u'Repeats by',
                description=u'Repeats on a specific day of the '
                            u'month or in a day of the week.',
                format='radio',
            ),
        ),

        LinesField(
            name='ordinalweek',
            schemata='default',
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
            name='bymonth',
            schemata='default',
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
            schemata='default',
            required=True,
            default=1,
            widget=atapi.IntegerWidget(
                label=u'Every',
                description=u'Repeats every day/week/month/year.',
            ),
        ),

        StringField(
            name='ends',
            schemata='default',
            default='ever',
            vocabulary=[
                (u'ever', u'No end date'),
                (u'count', u'End after a number of occurrences'),
                (u'until', u'End on a specific date'),
            ],
            widget=atapi.SelectionWidget(
                label=u'Range of recurrence',
                format='select',
            ),
        ),

        IntegerField(
            name='count',
            schemata='default',
            widget=atapi.IntegerWidget(
                label=u'Repeats For',
                description=u'Event repeats this number of times.',
            ),
        ),

        DateTimeField(
            name='until',
            schemata='default',
            widget=atapi.CalendarWidget(
                label=u'Repeats Until',
                description=u'Event repeats until this date.',
                show_hm=False,
            ),
        ),

    ]

    def __init__(self, extender, context):
        pass

    def getFields(self):
        return self.fields

    def getOrders(self):
        return [(10, 'recurrence')]
