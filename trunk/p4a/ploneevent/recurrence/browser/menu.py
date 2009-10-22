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
        results = []
        
        portal_state = getMultiAdapter((context, request), name='plone_portal_state')
        plone_utils = getToolByName(context, 'plone_utils')
        portal_url = portal_state.portal_url()

        results.append({ 'title'       : 'Edit this occurrence',
                         'description' : 'Remove this occurrence from the recurrence series and create a new event',
                         'action'      : context.absolute_url() + '/@@occurrence_edit',
                         'selected'    : False,
                         'icon'        : '',
                         'extra'       : {'id': 'delete-this-occurrence', 'separator': None, 'class': ''},
                         'submenu'     : None,
                         })
                          
        return results


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
        return True
