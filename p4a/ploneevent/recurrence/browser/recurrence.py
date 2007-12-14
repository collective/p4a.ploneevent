from zope.formlib import form
from Products.Five.formlib import formbase
from p4a.ploneevent.recurrence import interfaces

from p4a.datetimewidgets.widgets import DateWidget

class RecurrenceView(formbase.PageEditForm):
    """Calendar configuration.
    """

    form_fields = form.FormFields(interfaces.IRecurrenceSupport)
    form_fields["until"].custom_widget = DateWidget

