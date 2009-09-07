p4a.ploneevent Package Readme
=============================

Overview
--------
This package contains extensions to the standard Event of Plone.
Currently only the extension is included: Recurrence. 


Install
-------
p4a.ploneevent uses overrides.zcml, so make sure you add the following to your buildout.cfg

zcml = 
 p4a.ploneevent.recurrence.browser-overrides