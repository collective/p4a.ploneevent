from Products.Five.browser import BrowserView
from zope.interface import implements
from interfaces import IOccurrenceEditView
from Products.Archetypes.utils import addStatusMessage
from Products.Archetypes import PloneMessageFactory as _

from datetime import timedelta, datetime, time
from p4a.common.dtutils import DT2dt, dt2DT, gettz

from dateable import kalends

class OccurrenceEditView(BrowserView):

  implements(IOccurrenceEditView)
  
  def addDateExceptionToEvent(self,ordDt,event):
      """ Add ordinal date of this occurrence to exceptions list
          of original event
      """
      evExc = list(event.exceptions)
      evExc.append(ordDt)
      event.exceptions = tuple(evExc)
      
      #if exception date is same as start date, need to change start date
      #to date of next recurrence (does not already exist as an exception).
      if int(ordDt) == DT2dt(event.start()).toordinal():
        #find second ordinal date in index of occurrences
        recurrence = kalends.IRecurrence(event)
        occurDays = recurrence.getOccurrenceDays()
        #first list element will be first additional occurrence
        nextOccurrenceOrd = occurDays[0]
        iter = 0
        while str(occurDays[iter]) in event.exceptions:
            iter = iter + 1
        if iter>0 :
            nextOccurrenceOrd = occurDays[iter-1]
        (event.startDate, event.endDate) = self.offsetStartAndEndTimes(event, \
                                           nextOccurrenceOrd)
     
      event.reindexObject()         
      
  def copyEvent(self):
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
      return x
      
                
  def offsetStartAndEndTimes(self, evtObj, ordDt):
      """ Correct the start and end dates of the new occurrence """
      ordDt = int(ordDt)
      startDate = datetime.fromordinal(ordDt).replace(tzinfo=gettz())
      #XXX TODO factor time offset code so not duplicating code in browserview
      startDate = startDate + \
        timedelta(hours=evtObj.start().hour(),\
                  minutes=evtObj.start().minute())        
      endOffset = evtObj.end() - evtObj.start()            
      startDate = dt2DT(startDate)
      #XXX TODO otherwise returning 1 minute before 
      # appropriate end time, but could be done more elegantly
      endDate =  startDate + endOffset + 0.000001
      return (startDate,endDate)                   
           
  def deleteSingleOccurrence(self):
      """ Delete just this occurrence and redirect to 
        previous view.
      """
      # if we pass an ordinal date in the querystring delete that occurrence
      try:
        ordDt = self.context.request.r 
      # otherwise delete the first occurrence  
      except:
        ordDt = DT2dt(self.context.aq_self.start()).toordinal()
        
      #add date of deleted occurrence as exception to original
      self.addDateExceptionToEvent(str(ordDt),self.context.aq_self)
      
      strDt = dt2DT(datetime.fromordinal(int(ordDt)))
      status_message=_(u'You have deleted the occurrence of this event for %s.' % strDt)
      addStatusMessage(self.context.request,status_message)    
      self.context.request.RESPONSE.redirect(self.context.aq_self.absolute_url())
      
  def editSingleOccurrence(self):
      """ Create a new event as copy of original and redirect to 
          edit view for new event.
      """
      context = self.context

      # Cannot add an exception on a date that is not part of the recurrence
      listOrdinals = kalends.IRecurrence(context.aq_self).getOccurrenceDays()
      try:
        ordDt = self.context.request.r 
        if int(ordDt) not in listOrdinals:
            status_message =_(u"You attempted to make an exception on a " \
                              "date that is not a part of this event's " \
                              "series. Double-check the event and try again.")
            nextURL = context.aq_self.absolute_url()
            #return to original object with error msg
            addStatusMessage(context.request,status_message)
            context.request.RESPONSE.redirect(nextURL)            
      # otherwise delete the first occurrence  
      except:
        ordDt = DT2dt(self.context.aq_self.start()).toordinal()
              
      x = self.copyEvent()
      if x:
          # new event gets start date from passed ordinal or original start 
          # date.  if we pass an ordinal date in the querystring use as new 
          # start date
          if ordDt:
              (x.startDate,x.endDate) = self.offsetStartAndEndTimes(x,ordDt)
          else:
              ordDt = DT2dt(x.start()).toordinal()
        
          # add new date as exception to original
          self.addDateExceptionToEvent(str(ordDt),self.context.aq_self)

          # new event should not be recurring
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
      
          status_message=_(u'You created this new event as an exception ' \
                           'to the original recurring event series. The ' \
                           'original event will no longer have an ' \
                           'occurrence on the start date displayed below.' \
                           '  To ensure that an event occurrence exists ' \
                           'on this date, be sure to complete your edits ' \
                           'and hit the Save button. You may also want to ' \
                           'publish your new event.')
          xurl = x.absolute_url() 
          nextURL = xurl + '/edit'          

      #redirect to new object with portal status message      
      addStatusMessage(context.request,status_message)
      context.request.RESPONSE.redirect(nextURL)
    
  def editSubsequentOccurrences(self):
      """ Split this event into two recurrence series, and make changes to
          the subsequent occurrences.
      """        
      # fail if passed occurrence date is the same as the start date. 
      # TODO XXX :Perhaps a better way to do this would be to not show
      # the menu item if we are on the start date
      ordDt = getattr(self.context.request,'r',None)
      if not ordDt or \
       int(ordDt) == DT2dt(self.context.aq_self.start()).toordinal():
          status_message=_(u'To edit all occurrences, from the start date \
                             through all subsequent events, simply use this\
                             edit form.')
          addStatusMessage(self.context.request,status_message)
          url = self.context.aq_self.absolute_url()    
          self.context.request.RESPONSE.redirect(url + '/edit')
          return   
     
      ordDt = int(ordDt)
      
      # create new event as copy of original
      x = self.copyEvent()
      orig = self.context.aq_self
      if x:      
          #new event gets start date of passed-in occurrence date
          (x.startDate,x.endDate) =  self.offsetStartAndEndTimes(x,ordDt)
          
          #original event gets until value of day before passed-in occurrence
          dayBefore = ordDt-1 
          orig.until = dt2DT(datetime.fromordinal(dayBefore).replace(tzinfo=gettz()))
          
          #reindex original and new objects
          orig.reindexObject()
          x.reindexObject()

          #redirect to new object with portal status message      
          xurl = x.absolute_url() 
          status_message=_(u'You have split the original recurring event into \
                             two recurring events. You are now editing the new \
                             event. ')
          addStatusMessage(self.context.request,status_message)    
          self.context.request.RESPONSE.redirect(xurl + '/edit')
      else:
          raise          
             
    
    
    
    