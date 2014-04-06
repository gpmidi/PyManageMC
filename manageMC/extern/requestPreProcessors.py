#===============================================================================
# This file is part of PyManageMC.
#
#    PyManageMC is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    PyManageMC is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyManageMC.  If not, see http://www.gnu.org/licenses/old-licenses/gpl-2.0.html 
#===============================================================================
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
                  # Setting name => ( Default value, Template var name)
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


# def idStuff(request):
#     """ Add auth stuff """
#     from social.backends.google import GooglePlusAuth  # @UnresolvedImport
#     plus_scope = ' '.join(GooglePlusAuth.DEFAULT_SCOPE)
#     return {
#             'plus_scope':plus_scope,
#             'plus_id':settings.SOCIAL_AUTH_GOOGLE_PLUS_KEY,
#             }


