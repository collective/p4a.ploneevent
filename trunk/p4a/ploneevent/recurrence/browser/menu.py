from zope import interface
from zope.app.publisher.browser.menu import BrowserMenu, BrowserSubMenuItem
from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, queryMultiAdapter

from interfaces import IRecurrenceMenu, \
  IRecurrenceSubMenuItem

class RecurrenceMenu(BrowserMenu):
    interface.implements(IRecurrenceMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""        
        
        portal_state = getMultiAdapter((context, request), name='plone_portal_state')
        plone_utils = getToolByName(context, 'plone_utils')
        portal_url = portal_state.portal_url()
        try:
          qry = '?r=' + context.request.r
        except: 
          qry = ''  

        items = [{ 'title'         : 'Edit this event occurrence',
                   'description' : 'Remove this event from the recurrence series and make changes.',
                   'action'      : context.absolute_url() + '/@@occurrence_edit' + qry,
                   'selected'    : False,
                   'icon'        : '',
                   'extra'       : {'id': 'edit-this-occurrence', 'separator': None, 'class': ''},
                   'submenu'     : None,
                },

                  {'title'       : 'Delete this event occurrence',
                   'description' : 'Remove this event occurrence from the recurrence series',
                   'action'      : context.absolute_url() + '/@@occurrence_delete' + qry,
                   'selected'    : False,
                   'icon'        : '',
                   'extra'       : {'id': 'delete-this-occurrence', 'separator': None, 'class': ''},
                   'submenu'     : None,
                },
                
                {'title'       : 'Edit this and subsequent occurrences',
                 'description' : 'Split this event into two recurrence series, and make changes to \
                                  the subsequent occurrences.',
                 'action'      : context.absolute_url() + '/@@occurrence_editsubsequent' + qry,
                 'selected'    : False,
                 'icon'        : '',
                 'extra'       : {'id': 'edit-subsequent-occurrences', 'separator': None, 'class': ''},
                 'submenu'     : None,
                 },
                 
                 ]  
                          
        return items


class RecurrenceSubMenuItem(BrowserSubMenuItem):
    """ This class registers the submenu item beneath plone_contentmenu.
        The RecurrenceMenu BrowserMenu is the contents of this submenu item.
    """    
    interface.implements(IRecurrenceSubMenuItem)
    

    title = u'Recurrence options'
    description = u"Make exceptions and modify series or individual occurrences"
    submenuId = u'event_recurrence_menu'
    order = 8
    extra = {'id': 'recurrence-options-menu'}

    @property
    def action(self):
        # XXX FIXME
        return self.context.absolute_url()+ '/@@folder_listing'

    def available(self):
        # TODO: Answer question, "Shall this method call the base class' 
        # 'available' method as well, or is this sufficient?"
        if self.context.frequency == -1:
            return False
        return True
