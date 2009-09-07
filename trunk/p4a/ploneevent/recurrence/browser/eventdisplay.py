"""Occurrence rendering logic"""

from datetime import timedelta, datetime, time

from zope.interface import implements
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

from p4a.common import dtutils
from dateable.chronos.browser.eventdisplay import EventDisplay as ChEventDisplay
from dateable.chronos.browser.interfaces import IEventDisplay

class EventDisplay(ChEventDisplay):
    """Adapts en event to IEventDisplay
    """

    implements(IEventDisplay)

    def __init__(self, event, view):
        """Creates and calculates render information"""
        
        ChEventDisplay.__init__(self,event,view)
        eventord = event.start.toordinal()
        self.url = event.url + '?r=' + str(eventord)
        