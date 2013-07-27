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
# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.files import File
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.template.loader import render_to_string

# Celery
from celery.task import task  # @UnresolvedImport

# Built-in

# Mcer
from minecraft.models import *
from minecraft.serverType import getServerFromModel

@task(expires = 60 * 60)
def init(serverPK):
    """ Init the given server.  """
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    # Run the init 
    server.localInit()
    
@task(expires = 60 * 60)
def loadMap(serverPK, mapPK):
    """ Init the given server.  
    TODO: Add support for saving the existing map if one exists. 
    """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    mapSave = MapSave.objects.get(pk = mapPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    # Load the map
    server.localLoadMap(mapSave)
    
@task(expires = 60 * 60 * 24 * 14)
def save_map(serverPK, name, desc = '', version = '', owner = None):
    """ Save a map. Returns MapSave PK. """    
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    mapPK = server.localSaveMap(name = name, desc = desc, version = version, owner = owner)
    
    return mapPK 
    
@task(expires = 60 * 60 * 24)
def start(serverPK):
    """ Start a server """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    return server.localStartServer()
    
@task(expires = 60 * 60 * 24)
def stop(serverPK, warn = True, warnDelaySeconds = 0):
    """ Start a server """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    return server.localStopServer(warn = warn, warnDelaySeconds = warnDelaySeconds)

@task(expires = 60 * 60 * 24)
def restart(serverPK, warn = True, warnDelaySeconds = 0):
    """ Restart a server """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    results=dict(start=None,stop=None)
    results['stop'] = stop(
                           serverPK = mcServer.pk,
                           warn = warn,
                           warnDelaySeconds = warnDelaySeconds,
                           )

    # Make sure the stop worked
    if results['stop']:
        results['start'] = start(serverPK = mcServer.pk)
    return results

@task(expires = 60 * 60 * 24)
def say(serverPK, msg):
    """ Start a server """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    return server.localSay(msg = msg)
    
@task(expires = 60 * 60 * 24)
def status(serverPK):
    """ Start a server """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    return server.localStatus()
    
