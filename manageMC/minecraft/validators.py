'''
Created on Apr 5, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.core.exceptions import ValidationError
from extern.models import *


def validate_serverInstance(value):
    try:
        si = ServerInstance.objects.get(pk = value)
        if not si:
            raise ValidationError("Server instance %r doesn't exist" % value)
    except ServerInstance.DoesNotExist as e:
        raise ValidationError("Server instance %r doesn't exist" % value)