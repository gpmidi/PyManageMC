'''
Created on Apr 5, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.core.exceptions import ValidationError

from couchdbkit.exceptions import ResourceNotFound

from minecraft.models import *  # @UnusedWildImport
from extern.models import *  # @UnusedWildImport



def validate_serverInstance(value):
    try:
        si = ServerInstance.objects.get(pk=value)
        if not si:
            raise ValidationError("Server instance %r doesn't exist" % value)
    except ServerInstance.DoesNotExist as e:
        raise ValidationError("Server instance %r doesn't exist" % value)


def validate_serverBinary(value):
    try:
        from minecraft.models import MinecraftServerBinary
        si = MinecraftServerBinary.get(value)
        if not si:
            raise ValidationError("Server binary %r doesn't exist" % value)
    except ResourceNotFound as e:
        raise ValidationError("Server binary %r doesn't exist" % value)
