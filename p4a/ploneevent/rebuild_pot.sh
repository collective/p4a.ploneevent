#!/bin/bash 

DOMAIN="p4a.ploneevent"

touch locales/$DOMAIN.pot
i18ndude rebuild-pot --pot locales/$DOMAIN.pot --create $DOMAIN ./

# sync all locales
find locales -maxdepth 1 -mindepth 1 -type d \
     | grep -v .svn \
     | sed -e "s/locales\/\(.*\)$/\1/" \
     | xargs -I % i18ndude sync --pot locales/$DOMAIN.pot locales/%/LC_MESSAGES/$DOMAIN.po
