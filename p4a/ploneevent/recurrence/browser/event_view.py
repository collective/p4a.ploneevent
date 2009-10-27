from DateTime import DateTime
from p4a.common.dtutils import dt2DT
from p4a.common.dtutils import DT2dt

from dateable.kalends import IRecurrence
from dateable.kalends import IRecurringEvent
from Products.Five.browser import BrowserView

from p4a.ploneevent import PloneEventMessageFactory as _

CALVOCAB = {
    0: (_(u'year'), _(u'years')),
    1: (_(u'month'), _(u'months')),
    2: (_(u'week'), _(u'weeks')),
    3: (_(u'day'), _(u'days')),
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
        delta = DT2dt(self.context.end()) - DT2dt(self.context.start())
        return dt2DT(DT2dt(self.start()) + delta)

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
        if not IRecurringEvent.providedBy(self.context):
            return False
        rrule = self.rrule()
        if rrule is None:
            return False
        return True

    def rrule(self):
        return IRecurrence(self.context, None).getRecurrenceRule()

    def rrule_freq(self):
        rrule = self.rrule()
        if rrule is None:
            return ''
        freq = CALVOCAB[rrule._freq]
        if rrule._interval == 1:
            return freq[0]
        return freq[1]

    def rrule_interval(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._interval
        return 0

    def rrule_count(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._count
        return 0

    def rrule_end(self):
        rrule = self.rrule()
        if rrule is not None and rrule._until:
            return self.context.toLocalizedTime(dt2DT(rrule._until), long_format=0)
        return ''
