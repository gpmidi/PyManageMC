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
