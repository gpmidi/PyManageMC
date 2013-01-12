'''
Created on Jan 11, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.core.exceptions import ValidationError
import re


VALIDATE_HOSTNAME = re.compile(r'^[a-zA-Z0-9.\-]+$')
def validateHostIP(value):
    """ Make sure it's either a hostname or an IP 
    @warning: Does NOT check hostname resolution
    """
    if not VALIDATE_HOSTNAME.match(value):
        raise ValidationError(u'%r is not a hostname or an IP' % value)
    
