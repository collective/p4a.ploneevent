from zope.formlib import form
from Products.Five.formlib import formbase
from p4a.ploneevent.recurrence import interfaces

class RecurrenceView(formbase.PageEditForm):
    """Calendar configuration.
    """

    form_fields = form.FormFields(interfaces.IRecurrenceSchema)

    
class RecurrenceConfigView(formbase.PageEditForm):
    """Calendar configuration.
    """

    form_fields = form.FormFields(interfaces.IRecurrenceConfig)
    
