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
from django.core.exceptions import ValidationError
import re


VALIDATE_HOSTNAME = re.compile(r'^[a-zA-Z0-9.\-]+$')
def validateHostIP(value):
    """ Make sure it's either a hostname or an IP 
    @warning: Does NOT check hostname resolution
    """
    if not VALIDATE_HOSTNAME.match(value):
        raise ValidationError(u'%r is not a hostname or an IP' % value)
    
