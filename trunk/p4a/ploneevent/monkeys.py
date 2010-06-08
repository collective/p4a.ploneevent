from zope.schema import vocabulary

if not hasattr(vocabulary.SimpleVocabulary, 'fromDictionary'):

    def fromDictionary(cls, dict, *interfaces):
        """Construct a vocabulary from a list of (token, value) pairs.

        The order of the items is preserved as the order of the terms
        in the vocabulary.  Terms are created by calling the class
        method createTerm() with the pair (value, token).

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        terms = [cls.createTerm(token, token, value) for (token, value) in dict.items()]
        return cls(terms, *interfaces)
    fromDictionary = classmethod(fromDictionary)

    vocabulary.SimpleVocabulary.fromDictionary = fromDictionary

# XXX TODO: Fix this code in p4a.plonecalendar
from p4a.plonecalendar.eventprovider import TopicEventProvider

def getEvents(self, start=None, stop=None, **kw):
    #need to filter by topic criteria here too, to return correct
    #recurring events with _getEvents
    q = self.context.buildQuery()
    # drop any duplicate start and stop keyword args from
    # topic criteria as we are interested in start and stop of 
    # date range from calendar.
    if 'start' in q.keys():
         del(q['start'])
    if 'stop' in q.keys():
          del(q['stop'])
    kw.update(q)
    return self._getEvents(start=start, stop=stop, **kw)

TopicEventProvider.getEvents = getEvents


# Use portal's time formatting property for title_and_time
def eventDisplayInit(self, event, view):
    """Creates and calculates render information"""

    self.event = event
    self.view = view

    # XXX Check permissions
    self.viewable = True
    # TODO: Here we could calculate short titles that fit into one row
    # and how much of the decription fits and stuff like that as well.
    if self.viewable:
        self.title = event.title
        self.description = event.description
        self.url = event.url
    else:
        self.title = self.description = _('Private Event')
        self.url = ''

    event_begins = event.start
    event_ends = event.end
    site_properties = self.view.context.portal_properties.site_properties
    tf = site_properties.getProperty('localTimeOnlyFormat')
    tf = tf or site_properties.getProperty('localLongTimeFormat')
    
    #remove prefixed zeros which won't work with just strftime on some systems
    import re
    beginsStr = re.sub(r"\b0","",event_begins.strftime(tf))
    endsStr = re.sub(r"\b0","",event_ends.strftime(tf))
    self.title_and_time = "%s %s - %s" % (self.title, beginsStr, endsStr)
    
    
    
    