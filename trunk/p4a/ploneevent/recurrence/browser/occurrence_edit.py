from Products.Five.browser import BrowserView
from zope.interface import implements
from interfaces import IOccurrenceEditView
from Products.Archetypes.utils import addStatusMessage
from Products.Archetypes import PloneMessageFactory as _

from datetime import timedelta, datetime, time
from p4a.common.dtutils import DT2dt, dt2DT, gettz

class OccurrenceEditView(BrowserView):

  implements(IOccurrenceEditView)
  
  def addDateExceptionToEvent(self,ordDt,event):
    """ Add ordinal date of this occurrence to exceptions list
        of original event
    """
    evExc = list(event.exceptions)
    evExc.append(ordDt)
    event.exceptions = tuple(evExc)
    event.reindexObject()

  def editSingleOccurrence(self):
    """ Create a new event as copy of original and redirect to 
        edit view for new event.
    """
    idIncr = 1
    origId = self.context.aq_self.id
    exEvId = origId + '-' + str(idIncr)
    while getattr(self.context.aq_self.aq_parent,exEvId,None):
      idIncr = idIncr + 1
      exEvId = origId + '-' + str(idIncr)
    
    #get container
    f = self.context.aq_self.aq_parent
    
    #clone original Event object inside same container
    copyId = f.manage_pasteObjects(f.manage_copyObjects(origId))[0]['new_id']
    f.manage_renameObject(copyId,exEvId)
    
    x = getattr(f,exEvId,None)
    if x:

      #new event gets start date from passed ordinal or original start date
      try:
        # if we pass an ordinal date in the querystring use as new start date
        ordDt = self.context.request.r 
        startDate = datetime.fromordinal(int(ordDt)).replace(tzinfo=gettz())
        #XXX TODO factor time offset code so not duplicating code in browserview
        startDate = startDate + \
          timedelta(hours=x.start().hour(),\
                    minutes=x.start().minute())        
        endOffset = x.end() - x.start()            
        x.startDate = dt2DT(startDate)                
        #XXX TODO otherwise returning 1 minute before 
        # appropriate end time, but could be done more elegantly
        endDate =  x.startDate + endOffset + 0.000001
        x.endDate = endDate
         
      except:
        ordDt = DT2dt(x.start()).toordinal()
      #add new date as exception to original
      self.addDateExceptionToEvent(str(ordDt),self.context.aq_self)

      #new event should not be recurring
      x.frequency = -1
      x.interval = 1
      x.byweekday = None
      x.repeatday = []
      x.ends = False
      x.until = None
      x.count = None
      x.lingo = ''
      x.exceptions = ()

               
      #index new object
      x.reindexObject()
      
      
      #redirect to new object with portal status message      
      xurl = x.absolute_url() 
      status_message=_(u'You created this new event as an exception to the original \
                         recurring event series. The original event will no \
                         longer have an occurrence on the start date \
                         displayed below.  To ensure that an event occurrence \
                         exists on this date, be sure to complete your edits \
                         and hit the Save button.')
      addStatusMessage(self.context.request,status_message)    
      self.context.request.RESPONSE.redirect(xurl + '/edit')
      
