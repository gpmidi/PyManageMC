'''
Created on Jan 11, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.conf import settings


def gaProcessor(request):
    """ Add a Google Analytics tracking code """
    if hasattr(settings, 'GA_ACCOUNT'):    
        return {'gaAccount':settings.GA_ACCOUNT}
    return {'gaAccount':None}


def footerProcessor(request):
    """ Add an optional legal footer """
    if hasattr(settings, 'LEGAL_FOOTER'):    
        return {'legalFooter':settings.LEGAL_FOOTER}
    return {'legalFooter':None}


def siteInfoProcessor(request):
    """ Add an optional site info """
    INFOSETTINGS = {
                  # Setting name => ( Default value, Template name)
                  'SITE_HUMAN_NAME':("Minecraft Servers", 'SiteHumanName'),
                  "INTRO_TEXT":(None, 'IntroText'),
                  }
    ret = {}
    for settingName, info in INFOSETTINGS.items():
        if hasattr(settings, settingName):    
            ret[info[1]] = getattr(settings, settingName)
        else:
            ret[info[1]] = info[0]
    return ret

