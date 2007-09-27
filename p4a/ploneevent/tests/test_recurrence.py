from dateutil import rrule
from zope import interface
from Products.Five.testbrowser import Browser
from DateTime import DateTime
from Testing import ZopeTestCase
import datetime

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.Five import zcml

import p4a.common
import p4a.ploneevent
from p4a.ploneevent.recurrence import interfaces

ZopeTestCase.installProduct('CMFonFive')
PloneTestCase.setupPloneSite()

class RecurrenceTest(PloneTestCase.FunctionalTestCase):
    
    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)
        self.addProduct('CMFonFive')
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.ploneevent)

    def testRecurranceBasic(self):
        # Basic recurrence, daily for one year:
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')
        event.update(startDate = DateTime('2001/02/01 10:00'),
                     endDate = DateTime('2001/02/01 14:00'))
        
        # Set the recurrence info
        event.recurrence_frequency=rrule.DAILY
        event.recurrence_until=DateTime('2002/02/01')
        
        import pdb
        pdb.set_trace()
        recur = interfaces.IRecurringEvent(event)
        dates = recur.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 2).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2002, 2, 1).toordinal())
        self.failUnlessEqual(len(dates), 365)

    def testRecurranceMidnight(self):
        # Check that the recurrence works correctly with events starting
        # at midnight
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2001/02/01 00:00'),
                     endDate = DateTime('2001/02/01 04:00'))
        
        # Set the recurrence info
        event.recurrence_frequency=rrule.DAILY
        event.recurrence_until=DateTime('2001/02/04')
        
        recur = interfaces.IRecurringEvent(event)
        dates = recur.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 2).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2001, 2, 4).toordinal())
        self.failUnlessEqual(len(dates), 3)
        
    def test_ui(self):
        browser = Browser()
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        folder_url = self.folder.absolute_url() 
        
        # Add event
        browser.open(folder_url + '/createObject?type_name=Event')
        form = browser.getForm('event-base-edit')
        form.getControl(name='title').value = 'An Event'
        form.getControl(name='startDate_year').value = ['2007']
        form.getControl(name='startDate_month').value = ['04']
        form.getControl(name='startDate_day').value = ['01']
        form.getControl(name='startDate_hour').value = ['14']
        form.getControl(name='startDate_minute').value = ['00']
        form.getControl(name='endDate_year').value = ['2007']
        form.getControl(name='endDate_month').value = ['04']
        form.getControl(name='endDate_day').value = ['01']
        form.getControl(name='endDate_hour').value = ['14']
        form.getControl(name='endDate_minute').value = ['00']
        form.getControl(name='form_submit').click()        
        self.failUnlessEqual(browser.url, 
            folder_url + '/an-event?portal_status_message=Changes%20saved.')

        link = browser.getLink('Recurrence')
        link.click()


def test_suite():
    from unittest import TestSuite, makeSuite
    
    suite = TestSuite()
    suite.addTests(makeSuite(RecurrenceTest))
    suite.layer = layer.ZCMLLayer

    return suite

