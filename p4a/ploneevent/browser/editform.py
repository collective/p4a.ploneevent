from zope import interface
from zope import schema
from zope import component
from zope.formlib import form

from Products.CMFCore.utils import getToolByName

from p4a.form.editform import TabbedPageEditForm
from p4a.datetimewidgets.widgets import DatetimeWidget
from p4a.calendar.interfaces import IEvent
from p4a.plonecalendar.utils import dt2DT, DT2dt

class IEventEditForm(interface.Interface):
    """An event.
    """
    
    title = schema.TextLine(title=u'Title',
                            required=True)
    description = schema.Text(title=u'Description',
                              required=False)
    start = schema.Datetime(title=u'Start Time',
                            required=True)
    end = schema.Datetime(title=u'End Time',
                          required=False)
    timezone = schema.TextLine(title=u'Timezone',
                               required=True)
    type = schema.TextLine(title=u'Type',
                           required=True)


class ATEventAdapter(object):
    interface.implements(IEventEditForm)
    component.adapts(IEvent)
    
    def __init__(self, context):
        self.context = context
        putils = getToolByName(self.context, 'plone_utils')
        self.encoding = putils.getSiteEncoding()
        
    @property
    def title(self):
        return self.context.title_or_id()

    @property
    def description(self):
        return unicode(self.context.Description(),
                       self.encoding)
    
    @property
    def start(self):
        return DT2dt(self.context.start())

    @property
    def end(self):
        return DT2dt(self.context.end())
    
    @property
    def timezone(self):
        return self.context.start().timezone()

    @property
    def type(self):
        type = self.context.eventType
        # This is a tuple of unicode strings, typically.
        # We want just one string, so we take the first one.
        if type:
            return cmfutils.cookString(type[0])
        return ''

    
class EditForm(TabbedPageEditForm):
    """Main Editform
    """

    form_fields = form.FormFields(IEventEditForm)
    form_fields["start"].custom_widget = DatetimeWidget
    form_fields["end"].custom_widget = DatetimeWidget

