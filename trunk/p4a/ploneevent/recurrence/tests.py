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
        context.invokeFactory('Event', id)
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
        return browser                
    
    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)
        self.addProduct('CMFonFive')
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.ploneevent)
        zcml.load_config('configure.zcml', p4a.subtyper)

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
        browser = self.helperSetupBrowser()
        folder_url = self.folder.absolute_url() 
        
        # Add event
        browser.open(folder_url + '/createObject?type_name=Event')
        form = browser.getForm('event-base-edit')
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
        browser.open(folder_url + '/an-event/?r=732950')
        errStr = "Event view does not show correct start date for occurrence \
                  passed as query parameter."
        self.failUnless('Oct 01, 2007' in browser.contents, errStr)

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

    def testRecurrenceMenuAvailable(self):
        # Basic recurrence, daily for one year:
        context = self.folder
        eventSingle = self.helperCreateEvent(context, 'event-single')
        eventDouble = self.helperCreateEvent(context, 'event-double')
        recurrenceSingle = kalends.IRecurrence(eventSingle)
        recurrenceDouble = kalends.IRecurrence(eventDouble)

        # Set the recurrence info for the eventDouble to recur for one year
        eventDouble.frequency = rrule.DAILY
        eventDouble.ends = False  # True would mean the event repeats forever. 
        eventDouble.until = DateTime('2002/02/01')
        eventDouble.interval = 1
        eventDouble.count = None

        # Create browser and prepare for testing
        browser = self.helperSetupBrowser()      
        folder_url = context.absolute_url() 
        
        strMenuTest = 'Recurrence options'

        # Test to ensure recurrence options are not set for single events
        browser.open("%s/%s" % (folder_url, eventSingle.id))
        errStr = "Recurrence options submenu should not appear on events that" \
                 " do not have recurrence options set."
        self.failIf(strMenuTest in browser.contents, errStr)

        # Test to ensure recurrence options are indeed set for multiple events
        browser.open("%s/%s" % (folder_url, eventDouble.id))
        errStr = "Recurrence options submenu should indeed appear on events " \
                 "which have recurrence options set."
        self.failUnless(strMenuTest in browser.contents, errStr)
        
    def testCreateNewEventAsRecurrenceException(self):
    
        context = self.folder
        folder_url = self.folder.absolute_url() 
        
        recurEvent = self.helperCreateEvent(context, 'recurring-event')
        recurEvent.frequency = rrule.DAILY
        recurEvent.ends = False  # True would mean the event repeats forever. 
        recurEvent.until = DateTime('2002/02/01')
        recurEvent.interval = 1
        recurEvent.count = None    
    
        # Create browser and prepare for testing
        browser = self.helperSetupBrowser()
        
        # Create recurrence exception on January 30, 2001      
        editOccQry = "/@@occurrence_edit?r=730882"
        #browser.open("%s/%s%s" % (folder_url, recurEvent.id, editOccQry))
        
        #Test that we have created a new Event as copy of recurring Event
        errStr = "'Edit this event occurrence' did not create a new Event."
        newEvId = "recurring-event-1"
        #self.failUnless(newEvId in browser.url, errStr)
        
        #Test that we see appropriate portal status message
        errStr = "Correct portal status message does not display after  \
                  creating event exception with 'Edit this event occurrence'"
        strMsgTest = "You created this new event as an exception to the original"          
        #self.failUnless(strMsgTest in browser.contents, errStr)
        
        #Test that the start date of the new event is same as passed occurrence
        
        #Test that the start and end times 
        
        #Test that (some other) field values are the same
        
        #Test that the recurrence fields are set to default values
        
        
        
    """
    TESTS PSEUDOCODE
    [x] Is a new exception event being created?

    [x] Is a portal status message being displayed on the edit view of the new 
    exception event stating, 'You have now created an exception to the original
    event that cannot be undone. To ensure that an event occurrence exists on 
    this date, be sure to complete your edits and hit the Save button.'? 
     - I edited the message, but yes, check for that

    Is the ordinal date of occurrence being specified on the exceptions dates
     field of the original event?

    Is the p4a.ploneevent.recurrence.getOccurrenceDays method excluding the 
    dates in the new recurrence exception schema field from the index?

    Does creating an exception on a date that was never an occurrence on the 
     original event return an error?

    Does the new event have the same values as the original event, excluding
     recurrence parameters, and with the start date of the occurrence passed in?
        - NEW - This includes not copying the exception ordinal list

    Does the action ('edit this occurrence') appear in the recurrence options 
    dropdown menu only when an event is an occurrence of a recurring event?
    this is the menu item vs. the whole menu
    
    """


def test_suite():
    from unittest import TestSuite, makeSuite
    
    suite = TestSuite()
    suite.addTests(makeSuite(RecurrenceTest))
    suite.layer = layer.ZCMLLayer

    return suite
