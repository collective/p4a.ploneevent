import logging
from p4a.common import site

logger = logging.getLogger('p4a.ploneevent.sitesetup')

def setup_portal(portal):
    site.ensure_site(portal)
    setup_profile(portal)

def setup_profile(site):
    setup_tool = site.portal_setup
    setup_tool.setImportContext('profile-p4a.ploneevent:default')
    setup_tool.runAllImportSteps()
