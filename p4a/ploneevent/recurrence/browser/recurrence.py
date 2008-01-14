from zope.formlib import form
from p4a.form.editform import TabbedPageEditForm
from p4a.datetimewidgets.widgets import DateWidget

from p4a.ploneevent.recurrence import interfaces

class RecurrenceView(TabbedPageEditForm):
    """Recurrence view.
    """

    form_fields = form.FormFields(interfaces.IRecurrenceSupport)
    form_fields["until"].custom_widget = DateWidget

