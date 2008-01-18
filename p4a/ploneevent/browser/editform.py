from zope import interface
from zope import schema
from zope import component
from zope.formlib import form

from Products.CMFCore.utils import getToolByName

from p4a.form.editform import TabbedPageEditForm
from p4a.datetimewidgets.widgets import DatetimeWidget
from p4a.datetimewidgets.fields import DateTime
from p4a.calendar.interfaces import IEvent
from p4a.plonecalendar.utils import dt2DT, DT2dt

class IEventEditForm(interface.Interface):
    """An event.
    """
    
    title = schema.TextLine(title=u'Title',
                            required=True)
    description = schema.Text(title=u'Description',
                              required=False)
    startDate = DateTime(title=u'Start Time',
                            required=True)
    endDate = DateTime(title=u'End Time',
                          required=False)

    
class EditForm(TabbedPageEditForm):
    """Main edit form
    """
    form_fields = form.FormFields(IEventEditForm)

