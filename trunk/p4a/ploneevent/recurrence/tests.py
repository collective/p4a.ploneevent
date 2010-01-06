from dateutil import rrule
from zope import interface
from Products.Five.testbrowser import Browser
from DateTime import DateTime
from datetime import datetime
from Testing import ZopeTestCase
import datetime

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.Five import zcml

import p4a.common
import p4a.ploneevent
from dateable import kalends

from zExceptions import NotFound


PloneTestCase.setupPloneSite(products=("p4a.ploneevent",))

class RecurrenceTest(PloneTestCase.FunctionalTestCase):
    def helperCreateEvent(self, context, id, dtStart=None, dtEnd=None):
        """ Create a basic Plone event in 'context and mark it as a recurring 
        event. If no start and end dates are provided, helperCreateEvent 
        creates a default value for those parameters. Returns the new event 
        object itself. """
        if not dtStart:
            dtStart = DateTime('2001/02/01 10:00')
        if not dtEnd:
            dtEnd = DateTime('2001/02/01 14:00')
        context.invokeFactory('Event', id=id, title="My Basic Event")
        myEvent = getattr(context, id)
        myEvent.update(startDate=dtStart, endDate=dtEnd)
        interface.alsoProvides(myEvent, kalends.IRecurringEvent)
        return myEvent

    def helperTestLingo(self, iFrequency, iMonth, iDay, listStrTests, iWeek=-1):
        errStr = "'_buildRecurrenceString' did not properly generate '%s'."
        LIST_TEST_INTERVALS = [1,2,3,9,10,11]
        f = self.recurrence._buildRecurrenceString
        for i in LIST_TEST_INTERVALS:
            dt = DateTime(2009,iMonth,iDay,14,30,0)
            strResult = f(iFrequency, i, dt, iWeek)
            strControl = listStrTests[i]
            self.failUnless(strResult == strControl, errStr % strControl)
            
    def helperSetupBrowser(self):
        browser = Browser()
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        self.browser = browser
        return browser
    
    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)
        self.addProduct('CMFonFive')
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.ploneevent)
        zcml.load_config('configure.zcml', p4a.subtyper)
        self.helperSetupBrowser()

    def testRecurrenceBasic(self):
        # Basic recurrence, daily for one year:
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')
        event.update(startDate = DateTime('2001/02/01 10:00'),
                     endDate = DateTime('2001/02/01 14:00'))

        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
        recurrence = kalends.IRecurrence(event)

        # Set the recurrence info, to recur for one year
        event.frequency=rrule.DAILY
        event.ends = False #True would mean the event repeats forever. 
        event.until=DateTime('2002/02/01')
        event.interval = 1
        event.count = None
        
        # Test
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 2).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2002, 2, 1).toordinal())
        self.failUnlessEqual(len(dates), 365)
        
        # Try with an interval
        event.interval = 3
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 4).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2002, 1, 30).toordinal())
        self.failUnlessEqual(len(dates), 121)

        # Have a max count:
        # count overrides until
        event.count = 25         
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(len(dates), 24)

    def testRecurrenceMidnight(self):
        # Check that the recurrence works correctly with events starting
        # at midnight
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2001/02/01 00:00'),
                     endDate = DateTime('2001/02/01 04:00'))
        
        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
        recurrence = kalends.IRecurrence(event)

        # Set the recurrence info
        event.frequency=rrule.DAILY
        event.until=DateTime('2001/02/04')
        event.interval=1
        event.count=None
        
        # Test
        dates = recurrence.getOccurrenceDays()        
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 2).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2001, 2, 4).toordinal())
        self.failUnlessEqual(len(dates), 3)

    def testRecurrenceWeek(self):
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2007/02/01 00:00'),
                     endDate = DateTime('2007/02/01 04:00'))
        
        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
        recurrence = kalends.IRecurrence(event)

        # Set the recurrence info
        event.frequency=rrule.WEEKLY
        event.until=DateTime('2008/02/04')
        event.interval=1
        event.count=None
        
        # Test
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2007, 2, 8).toordinal())
        self.failUnlessEqual(dates[1], datetime.date(2007, 2, 15).toordinal())
        self.failUnlessEqual(dates[2], datetime.date(2007, 2, 22).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2008, 1, 31).toordinal())
        self.failUnlessEqual(len(dates), 52)
        
    def test_recurrence(self):
        folder_url = self.folder.absolute_url() 
        
        # Add event
        self.browser.open(folder_url + '/createObject?type_name=Event')
        form = self.browser.getForm('event-base-edit')
        form.getControl(name='title').value = 'An Event'
        form.getControl(name='startDate_year').value = ['2007']
        form.getControl(name='startDate_month').value = ['04']
        form.getControl(name='startDate_day').value = ['01']
        form.getControl(name='startDate_hour').value = ['11']
        form.getControl(name='startDate_minute').value = ['00']
        form.getControl(name='endDate_year').value = ['2007']
        form.getControl(name='endDate_month').value = ['04']
        form.getControl(name='endDate_day').value = ['01']
        form.getControl(name='endDate_hour').value = ['11']
        form.getControl(name='endDate_minute').value = ['00']
        # Edit the recurrence info:
        form.getControl(name='frequency').value = ['1']
        form.getControl(name='interval').value = '6'
        form.getControl(name='form_submit').click()
        
        # Make sure it's properly indexed:
        cat = self.portal.portal_catalog
        self.failUnless(len(cat(portal_type='Event', recurrence_days=732950)) == 1)
        
        # Test that we can browse to the event passing a recurrence day
        # and see that the date shows for the recurrence, not the original event
        # 732950 = (2007/10/01)
        self.browser.open(folder_url + '/an-event/?r=732950')
        errStr = "Event view does not show correct start date for occurrence \
                  passed as query parameter."
        self.failUnless('Oct 01, 2007' in self.browser.contents, errStr)

    def testLingo(self):
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
        self.recurrence = kalends.IRecurrence(event)

        STR_YEARLY_TESTS = ['',
            'Every year on June 23rd',
            'Every two years on June 23rd',
            'Every three years on June 23rd','','','','','',
            'Every nine years on June 23rd',
            'Every 10 years on June 23rd',
            'Every 11 years on June 23rd',
        ]
        self.helperTestLingo(0, 6, 23, STR_YEARLY_TESTS)
        
        STR_MONTHLY_TESTS_2ND_TUESDAY = ['',
            'Every month on the 2nd Tuesday',
            'Every two months on the 2nd Tuesday',
            'Every three months on the 2nd Tuesday','','','','','',
            'Every nine months on the 2nd Tuesday',
            'Every 10 months on the 2nd Tuesday',
            'Every 11 months on the 2nd Tuesday',
        ]
        self.helperTestLingo(1, 6, 9, STR_MONTHLY_TESTS_2ND_TUESDAY, 2)
        
        STR_MONTHLY_TESTS_11TH_DAY = ['',
            'Every month on the 11th day',
            'Every two months on the 11th day',
            'Every three months on the 11th day','','','','','',
            'Every nine months on the 11th day',
            'Every 10 months on the 11th day',
            'Every 11 months on the 11th day',
        ]
        self.helperTestLingo(1, 6, 11, STR_MONTHLY_TESTS_11TH_DAY)
            
        STR_WEEKLY_TESTS = ['',
            'Every week on Saturday',
            'Every two weeks on Saturday',
            'Every three weeks on Saturday','','','','','',
            'Every nine weeks on Saturday',
            'Every 10 weeks on Saturday',
            'Every 11 weeks on Saturday',
        ]
        self.helperTestLingo(2, 6, 13, STR_WEEKLY_TESTS)
        
        STR_DAILY_TESTS = ['',
            'Every day',
            'Every two days',
            'Every three days','','','','','',
            'Every nine days',
            'Every 10 days',
            'Every 11 days',
        ]
        self.helperTestLingo(3, 6, 11, STR_DAILY_TESTS)

    def testGetWeekInMonthFromDate(self):
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
        self.recurrence = kalends.IRecurrence(event)
        errStr = "getWeekInMonthFromDate failed to return the proper week index"

        dt = datetime.datetime(2009,12,28,14,30,0)
        iWeekFourthMonday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekFourthMonday == 4, errStr)
        
        dt = datetime.datetime(2009,12,29,14,30,0)
        iWeekFifthTuesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekFifthTuesday == 5, errStr)

        dt = datetime.datetime(2010,1,6,14,30,0)
        iWeekFirstWednesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekFirstWednesday == 1, errStr)

        dt = datetime.datetime(2010,2,3,14,30,0)
        iWeekFirstWednesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekFirstWednesday == 1, errStr)

        dt = datetime.datetime(2010,1,19,14,30,0)
        iWeekThirdTuesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekThirdTuesday == 3, errStr)

        dt = datetime.datetime(2010,2,16,14,30,0)
        iWeekThirdTuesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekThirdTuesday == 3, errStr)

        dt = datetime.datetime(2010,1,27,14,30,0)
        iWeekFourthWednesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekFourthWednesday == 4, errStr)

        dt = datetime.datetime(2010,2,24,14,30,0)
        iWeekFourthWednesday = self.recurrence.getWeekInMonthFromDate(dt)
        self.failUnless(iWeekFourthWednesday == 4, errStr)

        dt = datetime.datetime(2009,12,29,14,30,0)
        iWeekFourthWednesday = self.recurrence.getWeekInMonthFromDate(dt)
        # TODO: Figure out what the failUnless here was/is supposed to be, or 
        # decide not to have this part of the test and delete.        

    def testRecurrenceMenu(self):
        # Basic recurrence, daily for one year:
        context = self.folder
        eventSingle = self.helperCreateEvent(context, 'event-single')
        eventMultiple = self.helperCreateEvent(context, 'event-double')
        recurrenceSingle = kalends.IRecurrence(eventSingle)
        recurrenceMultiple = kalends.IRecurrence(eventMultiple)

        # Set the recurrence info for the eventDouble to recur for one year
        eventMultiple.frequency = rrule.DAILY
        eventMultiple.ends = False  # True would mean the event repeats forever. 
        eventMultiple.until = DateTime('2002/02/01')
        eventMultiple.interval = 1
        eventMultiple.count = None

        # Prepare for testing
        folder_url = context.absolute_url() 
        
        strMenuTest = 'Recurrence options'
        strMenuItemTest = 'Edit this event occurrence'

        # Test to ensure recurrence options are not set for single events
        self.browser.open("%s/%s" % (folder_url, eventSingle.id))
        errStr = "Recurrence options submenu should not appear on events that" \
                 " do not have recurrence options set."
        self.failIf(strMenuTest in self.browser.contents, errStr)

        errStr = "Edit this occurrence menu item should not appear on events " \
                 "that do not have recurrence options set."
        self.failIf(strMenuItemTest in self.browser.contents, errStr)

        # Test to ensure recurrence options are indeed set for multiple events
        self.browser.open("%s/%s" % (folder_url, eventMultiple.id))
        errStr = "Recurrence options submenu should indeed appear on events " \
                 "which have recurrence options set."
        self.failUnless(strMenuTest in self.browser.contents, errStr)
        
        errStr = "Edit this occurrence menu item should indeed appear on " \
                 "events which have recurrence options set."
        self.failUnless(strMenuItemTest in self.browser.contents, errStr)
        
    def testCreateNewEventAsRecurrenceException(self):
        """ Create an exception, then make sure new (duplicated) event
            is created for that exception date.
        """
        context = self.folder
        folder_url = self.folder.absolute_url() 
        
        recurEvent = self.helperCreateEvent(context, 'recurring-event')
        recurEvent.frequency = rrule.DAILY
        recurEvent.ends = False  # True would mean the event repeats forever. 
        recurEvent.until = DateTime('2002/02/01')
        recurEvent.interval = 1
        recurEvent.count = None
        self.failUnless('recurring-event' in context.objectIds())
        
        # Create recurrence exception on February 1, 2002
        strNewEventOrdinal = '730882'
        editOccQry = "/@@occurrence_edit?r=%s" % strNewEventOrdinal
        self.browser.open("%s/%s%s" % (folder_url, recurEvent.id, editOccQry))
        
        # Test that we have created a new Event as copy of recurring Event
        errStr = "'Edit this event occurrence' did not create a new Event."
        newEvId = "recurring-event-1"
        self.failUnless(newEvId in context.objectIds(), errStr)
        
        # Test that we see appropriate portal status message
        errStr = "Correct portal status message does not display after  \
                  creating event exception with 'Edit this event occurrence'"
        strMsgTest = "You created this new event as an exception to the original"
        self.failUnless(strMsgTest in self.browser.contents, errStr)
        
        # Test that the start date of the new event is same as passed occurrence
        # and so is end date. And make sure repeat is off.
        newEvent = context[newEvId]
        self.failUnless(newEvent.startDate == DateTime('2002/02/01 10:00:00 GMT-8'))
        self.failUnless(newEvent.endDate == DateTime('2002/02/01 14:00:00.086 GMT-8'))
        self.failUnless(newEvent.frequency == -1)   # is repeat off?       
        
        # Is the ordinal date of occurrence being specified on the exceptions
        # dates field of the original event?
        errStr = "Didn't find our exception in the list"
        self.failUnless(strNewEventOrdinal in recurEvent.exceptions, errStr)
        errStr = "Shouldn't find an exception in the list of the new object"
        self.failIf(strNewEventOrdinal in newEvent.exceptions, errStr)

        # Is the p4a.ploneevent.recurrence.getOccurrenceDays method excluding 
        # the dates in the new recurrence exception schema field from the index?
        recurrenceNewEvent = kalends.IRecurrence(newEvent)
        recurrenceRecurEvent = kalends.IRecurrence(recurEvent)
        listNewOccurrences = recurrenceNewEvent.getOccurrenceDays()
        listRecurOccurrences = recurrenceRecurEvent.getOccurrenceDays()
        errStr = "New exception occurrence should not have itself any " \
                 "occurrences"
        self.failUnless(len(listNewOccurrences) == 0, errStr)
        errStr = "Original recurring event should no longer be reporting an " \
                 "occurrence for the new exception event."
        self.failIf(strNewEventOrdinal in listRecurOccurrences, errStr)
        
        #Are the recurrence fields on the new event set to default values?
        self.failUnless(newEvent.frequency == -1)
        self.failUnless(newEvent.interval == 1)
        self.failUnless(newEvent.byweekday == None)
        self.failUnless(newEvent.repeatday == [])
        self.failUnless(newEvent.ends == False)
        self.failUnless(newEvent.until == None)
        self.failUnless(newEvent.count == None)
        self.failUnless(newEvent.lingo == '')
        self.failUnless(newEvent.exceptions == ())
        
        #Verify that the title of the new event is the same as old
        self.failUnless(newEvent.title == 'My Basic Event')
        
    def testCreateNewEventAsRecurrenceException_FirstInSeries(self):
        """ Let's make an exception on the FIRST date of the recurring event
            and make sure things work ok.
        """
        self.fail("Need to implement")

    def testCreateNewEventAsRecurrenceException_LastInSeries(self):
        """ Let's make an exception on the LAST date of the recurring event
            (that ends on a specific date) and make sure things work ok.
        """
        self.fail("Need to implement")

    def testCreateNewEventWithNonExistantOccurrence(self):
        """ Does creating an exception on a date that was never an occurrence on the 
        original event return an error?
        """
        context = self.folder
        folder_url = self.folder.absolute_url() 
        
        recurEvent = self.helperCreateEvent(context, 'recurring-event')
        recurEvent.frequency = rrule.DAILY
        recurEvent.ends = False  # True would mean the event repeats forever. 
        recurEvent.until = DateTime('2002/02/01')
        recurEvent.interval = 1
        recurEvent.count = None
        self.failUnless('recurring-event' in context.objectIds())
    
        # Create recurrence exception on a day not in the recurrence
        strNewEventOrdinal = '730883'
        editOccQry = "/@@occurrence_edit?r=%s" % strNewEventOrdinal
        self.browser.open("%s/%s%s" % (folder_url, recurEvent.id, editOccQry))

        # Ensure there is a portal status message
        strMsgTest = "You attempted to make an exception on a date that is not "
        errStr = "There was no indication that user cannot create exception now"
        self.failUnless(strMsgTest in self.browser.contents, errStr)
        
        # Be sure we have not created a new Event as copy of recurring Event
        errStr = "Accidentally created new Event on non-existent occurrence"
        newEvId = "recurring-event-1"
        self.failIf(newEvId in context.objectIds(), errStr)

    def testDeleteOccurrenceInRecurrenceEvent(self):
        """ Delete a single exception for this recurring event.
        """
        context = self.folder
        folder_url = self.folder.absolute_url() 

        recurEvent = self.helperCreateEvent(context, 'recurring-event')
        recurEvent.frequency = rrule.DAILY
        recurEvent.ends = False  # True would mean the event repeats forever. 
        recurEvent.until = DateTime('2002/02/01')
        recurEvent.interval = 1
        recurEvent.count = None
        self.failUnless('recurring-event' in context.objectIds())

        # Delete recurrence on February 1, 2002
        editOccQry = "/@@occurrence_delete?r=730882"
        self.browser.open("%s/%s%s" % (folder_url, recurEvent.id, editOccQry))
        
        #Test that we see appropriate portal status message
        errStr = "Correct portal status message does not display"
        strMsgTest = "You have deleted the occurrence of this event"
        self.failUnless(strMsgTest in self.browser.contents, errStr)

        # There should be no new events created from this
        self.failUnless(len(context.objectIds()) == 1, "There should only be our recurring event")

        # Is this event in the exception list now?
        self.failUnless("730882" in recurEvent.exceptions,"Didn't find our exception in the list")
        
    def testDeleteOccurrenceInRecurrenceEvent_IfThereIsOnlyOneOccurrence(self):
        """ Edge case: Delete a single exception for this recurring event, but
            the recurring event only has one occurrence.
        """
        self.fail("Need to implement")
    
    def testIncorrectQueryParameter(self):
        context = self.folder
        folder_url = self.folder.absolute_url() 
        recurEvent = self.helperCreateEvent(context, 'my-event')
        recurEvent.frequency = rrule.DAILY
        recurEvent.ends = False  # True would mean the event repeats forever. 
        recurEvent.until = DateTime('2002/02/01')
        recurEvent.interval = 1
        recurEvent.count = None    
        strMsgTest = "We're sorry, but that page doesn't exist"
        
        # Ensure that we can view the start date occurrence
        viewOccQry = "/?r=730517"
        self.browser.open("%s/%s%s" % (folder_url, recurEvent.id, viewOccQry))
        errStr = "Should be able to view a the start date of an Event"
        self.failUnless('My Basic Event' in self.browser.contents, errStr)

        # Ensure that we can view one of the non-start date occurrences
        viewOccQry = "/?r=730518"
        self.browser.open("%s/%s%s" % (folder_url, recurEvent.id, viewOccQry))
        errStr = "Should be able to view a non-start date occurrence"
        self.failUnless('My Basic Event' in self.browser.contents, errStr)

        # Ensure we raise a 404 Error when the query parameter is incorrect
        viewOccQry = "/?r=730883"
        strRequest = "%s/%s%s" % (folder_url, recurEvent.id, viewOccQry)
        bNotFound = False
        try:
            self.browser.open(strRequest)
        except:
            # Using bare except because neither self.assertRaises nor a specific 
            # except, will catch the exception
            bNotFound = True
        errStr = "404 Error was not raised when the query parameter is incorrect"
        self.failUnless(bNotFound, errStr)
        
    def testEditThisAndSubsequentOccurrences(self):
        """ Edit the present and future occurrences of a recurring event """

        context = self.folder
        folder_url = self.folder.absolute_url() 

        recurEvent = self.helperCreateEvent(context, 'recurring-event')
        recurEvent.frequency = rrule.DAILY
        recurEvent.ends = False  # True would mean the event repeats forever. 
        recurEvent.until = DateTime('2002/02/01')
        recurEvent.interval = 1
        recurEvent.count = None
        self.failUnless('recurring-event' in context.objectIds())

        # Edit recurrence on January 30, 2002 and subsequent occurrences
        editOccQry = "/@@occurrence_editsubsequent?r=730880"
        self.browser.open("%s/%s%s" % (folder_url, recurEvent.id, editOccQry))
        
        # Test that we have created a new Event as copy of recurring Event
        errStr = "'Edit this and subsequent occurrences' did not create a new\
                   Event."
        newEvId = "recurring-event-1"
        newEv = getattr(context,newEvId)
        self.failUnless(newEvId in context.objectIds(), errStr)
        
        #Ensure that old event has an until value of day before specified occurrence
        errStr = "'Edit this and subsequent occurrences' did not correctly set the \
                   value of 'until' field on original event."
        dayBefore = DateTime('2002/01/29')           
        self.failUnless(recurEvent.until == dayBefore, errStr)
        
        #Ensure that new event has same recurrence field values as original,
        #other than until
        errStr = "The values for recurrence fiels in the new event created by \
                  'Edit this and subsequent occurrences' do not match those of \
                  the original event."
        self.failUnless(newEv.frequency == recurEvent.frequency, errStr)
        self.failUnless(newEv.ends == recurEvent.ends, errStr)
        self.failUnless(newEv.interval == recurEvent.interval, errStr)
        self.failUnless(newEv.count == recurEvent.count, errStr)        
        
        #Ensure that the new event has a start date of the specified occurrence
        errStr = "The start date of the new event created by 'edit this and \
                  subsequent events' is not the same as the occurrence used \
                  for the split date."
        self.failUnless(newEv.startDate == DateTime('2002/01/30 10:00:00 GMT-8') , errStr)
        
        #Ensure we see the appropriate portal status message?
        # TODO: Find out if there is more that needed to be tested here due to
        # this comment, or get rid of the comment if not needed.


def test_suite():
    from unittest import TestSuite, makeSuite
    
    suite = TestSuite()
    suite.addTests(makeSuite(RecurrenceTest))
    suite.layer = layer.ZCMLLayer

    return suite
