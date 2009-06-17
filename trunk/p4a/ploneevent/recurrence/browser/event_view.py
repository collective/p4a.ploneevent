from zope.i18n import translate
from Products.Five.browser import BrowserView
from dateable.kalends import IRecurringEvent, IRecurrence
from p4a.common.dtutils import dt2DT
from kss.core import KSSView, kssaction
from DateTime import DateTime

FREQ = {
    0: 'year',
    1: 'month',
    2: 'week',
    3: 'day',
    4: 'hour',
    5: 'minute',
    6: 'second',
}

CALVOCAB = {
    0: ('year', 'years'),
    1: ('month', 'months'),
    2: ('week', 'weeks'),
    3: ('day', 'days'),
}


class EventView(BrowserView):

    def start(self):
        date = DateTime(self.context.start())
        if self.isRecurring() and self.request.form.has_key('date'):
            current = DateTime(self.request.form['date'])
            parts = list(date.parts())
            parts[0] = current.year()
            parts[1] = current.month()
            parts[2] = current.day()
            date = DateTime(*parts)
        return date

    def end(self):
        offset = self.context.end() - self.context.start()
        return self.start() + offset

    def same_day(self):
        return self.context.start().Date() == self.context.end().Date()

    def short_start_date(self):
        return self.context.toLocalizedTime(self.start(), long_format=0)

    def long_start_date(self):
        return self.context.toLocalizedTime(self.start(), long_format=1)

    def start_time(self):
        return self.start().strftime(self.time_format())

    def short_end_date(self):
        return self.context.toLocalizedTime(self.end(), long_format=0)

    def long_end_date(self):
        return self.context.toLocalizedTime(self.end(), long_format=1)

    def end_time(self):
        return self.end().strftime(self.time_format())

    def datetime_format(self):
        site_properties = self.context.portal_properties.site_properties
        return site_properties.getProperty('localLongTimeFormat')

    def date_format(self):
        site_properties = self.context.portal_properties.site_properties
        return site_properties.getProperty('localTimeFormat')

    def time_format(self):
        datetime_format = self.datetime_format()
        if '%p' in datetime_format:
            # Using AM/PM:
            return ' '.join(datetime_format.split(' ')[-2:])
        # 24 H format
        return datetime_format.split(' ')[-1]

    def isRecurring(self):
        return IRecurringEvent.providedBy(self.context)

    def rrule(self):
        return IRecurrence(self.context, None).getRecurrenceRule()

    def rrule_freq(self):
        rrule = self.rrule()
        if rrule is None:
            return ''
        if rrule._interval == 1:
            text = u"Every ${frequency}"
        else:
            text = u"Every ${interval} ${frequency}s"

        return translate(text, mapping={'interval':rrule._interval,
                                        'frequency':FREQ[rrule._freq]})
    def rrule_interval(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._interval
        return 0

    def rrule_end(self):
        rrule = self.rrule()
        if rrule is not None and rrule._until:
            return self.context.toLocalizedTime(dt2DT(rrule._until), long_format=0)
        return ''


class RecurrenceView(KSSView):

    @kssaction
    def updateRecurUI(self, frequency=-1, interval=0, ends=0):
        ends = int(ends)
        interval = int(interval)
        frequency = int(frequency)
        core = self.getCommandSet('core')

        # Range of recurrence
        if frequency == -1:
            core.setStyle('#archetypes-fieldname-ends', name='display', value='none')
            core.setStyle('#archetypes-fieldname-count', name='display', value='none')
            core.setStyle('#archetypes-fieldname-until', name='display', value='none')
        else:
            core.setStyle('#archetypes-fieldname-ends', name='display', value='block')
            if not ends:
                core.setStyle('#archetypes-fieldname-count', name='display', value='none')
                core.setStyle('#archetypes-fieldname-until', name='display', value='none')
            elif ends == 1:
                core.setStyle('#archetypes-fieldname-count', name='display', value='block')
                core.setStyle('#archetypes-fieldname-until', name='display', value='none')
            elif ends == 2:
                core.setStyle('#archetypes-fieldname-count', name='display', value='none')
                core.setStyle('#archetypes-fieldname-until', name='display', value='block')

        # Montly Repeat Day
        if frequency == 1:
            core.setStyle('#archetypes-fieldname-repeatday', name='display', value='block')
        else:
            core.setStyle('#archetypes-fieldname-repeatday', name='display', value='none')

        # By Week
        if frequency == 2:
            core.setStyle('#archetypes-fieldname-byweek', name='display', value='block')
        else:
            core.setStyle('#archetypes-fieldname-byweek', name='display', value='none')

        # Interval
        if frequency == -1:
            caltext = 'day/week/month/year.'
            interval = ''
            display = 'none'
        elif interval > 1:
            caltext = CALVOCAB[frequency][1]
            display = 'block'
        elif interval == 0:
            caltext = 'day/week/month/year.'
            interval = ''
            display = 'block'
        else:
            caltext = CALVOCAB[frequency][0]
            interval = ''
            display = 'block'

        content = 'Repeats every %s %s.' % (interval, caltext)
        core.replaceInnerHTML('#interval_help', content)
        core.setStyle('#archetypes-fieldname-interval', name='display', value=display)
