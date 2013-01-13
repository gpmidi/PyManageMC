# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.files import File
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from celery.task import task #@UnresolvedImport
from django.template.loader import render_to_string





# Built-in

# Mcer
from mcer.minecraft.models import *
from mcer.minecraft.serverType import getServerFromModel

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
def stop(serverPK):
    """ Start a server """
    # Get model objects
    mcServer = MinecraftServer.objects.get(pk = serverPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
    
    return server.localStopServer()
    
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
    
