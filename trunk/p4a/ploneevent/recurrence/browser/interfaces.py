from zope import interface
from zope.app.publisher.interfaces.browser import IBrowserMenu, \
                                                  IBrowserSubMenuItem

class IRecurrenceMenu(IBrowserMenu):
    """Actions for recurring events.
    """
class IRecurrenceSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the recurrence menu.
    """
class IOccurrenceEditView(interface.Interface):
    """ BrowserView with methods to handle editing and deletion of 
        single and multiple occurrences from a recurring event series.
    """
        
