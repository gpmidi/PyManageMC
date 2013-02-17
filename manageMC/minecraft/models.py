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
from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.contrib import admin
import os.path
# Load serverType objects
from minecraft.serverType import loadOtherServerTypes, allServerTypes

class MinecraftServerBinary(models.Model):
    """ A type of Minecraft server a a specific version """
    typeName = models.CharField(
                                null = False,
                                blank = False,
                                max_length = 255,
                                db_index = True,
                                verbose_name = "Name",
                                help_text = "Name of the server type",
                                choices = (
                                              # (TYPE string, human name),
                                              ('Stock', 'Stock'),
                                              ('Bukkit', 'Bukkit'),
                                              ('Tekkit', 'Tekkit'),
                                              ('NerdBukkit', 'NerdBukkit'),
                                              ('FTB', "Feed The Beast"),
                                           ),
                                )
    exc = models.FileField(
                           null = True,
                           blank = False,
                           max_length = 4096,
                           upload_to = "srv/jars/%Y/%m/%d/",
                           verbose_name = "Exec",
                           help_text = "The binary JAR file",
                           )
    files = models.FileField(
                               null = True,
                               blank = True,
                               max_length = 4096,
                               upload_to = "srv/files/%Y/%m/%d/",
                               verbose_name = "Support Files - Overwrite",
                               help_text = "A ZIP file containing any supporting files. Will overwrite any existing files with the same name/path. ",
                               )    
    version = models.CharField(
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Version",
                            help_text = "Version of the binary",
                            )
    releaseStatus = models.CharField(
                                null = False,
                                blank = False,
                                max_length = 255,
                                verbose_name = "Release Status",
                                help_text = "This server version release type",
                                choices = (
                                              # (TYPE string, human name),
                                              ('Production Release', 'Production Release'),
                                              ('Dev Build', 'Dev Build'),
                                              ('Mature Release', 'Mature Release'),
                                              ('Nightly Dev Build', 'Nightly Dev Build'),
                                              ('Pre-release', 'Pre-release'),
                                              ('Beta', 'Beta'),
                                              ('Alpha', 'Alpha'),
                                           ),
                                )
    created = models.DateTimeField(
                                    null = False,
                                    auto_now_add = True,
                                    editable = False,
                                    verbose_name = "Date Created",
                                    help_text = "The date that this server bin was first defined",
                                    )
    modified = models.DateTimeField(
                                    null = False,
                                    auto_now = True,
                                    editable = False,
                                    verbose_name = "Date Modified",
                                    help_text = "The date that this server bin was last modified",
                                    )
    
    def __str__(self):
        return "MCServerBin %s_%s" % (self.name, self.version)
    
    def __repr__(self):
        return "<MCServerBin_%s_%s>" % (self.name, self.version)
    
admin.site.register(MinecraftServerBinary)
                  
class MinecraftServer(models.Model):
    """ A standard Minecraft server """
    name = models.CharField(
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            editable = False,
                            verbose_name = "Name",
                            help_text = "Name of this server",
                            )
    bin = models.ForeignKey(
                             MinecraftServerBinary,
                             db_index = True,
                             verbose_name = "Server Binary",
                             help_text = "The type/version of server to run",
                             )
    created = models.DateTimeField(
                                    null = False,
                                    auto_now_add = True,
                                    editable = False,
                                    verbose_name = "Date Created",
                                    help_text = "The date that this server was created",
                                    )
    modified = models.DateTimeField(
                                    null = False,
                                    auto_now = True,
                                    editable = False,
                                    verbose_name = "Date Modified",
                                    help_text = "The date that this server object was last modified",
                                    )
    instance = models.OneToOneField(
                                    'extern.ServerInstance',
                                    null = False,
                                    db_index = True,
                                    editable = False,
                                    verbose_name = "Server Instance",
                                    # help_text="",
                                    )
    
    def __str__(self):
        return "MCServer_%s_%s" % (self.name, self.getSessionName())
    
    def __repr__(self):
        return "<MCServer %r %r>" % (self.name, self.getSessionName())
        
    def loc(self):
        """ Return the full path to the server """
        return os.path.join(settings.MC_SERVER_PATH, str(self.getSessionName()))
    
    def getSessionName(self):
        """ Returns the screen session name. 
        Must NEVER change. 
        """
        return "MC-%d" % self.pk

admin.site.register(MinecraftServer)

# class PublicMapSave(models.Model):
#    """ Allow users to save maps. 
#    Note: Map files are NOT private. 
#    Note: The zip must be in the following structure
#    FIXME: Does it have to be named world? Any support for importing ones not named world?
#        /world/<map data>
#        /world_nether/<map data>         ** optional **
#        /world_the_end/<map data>         ** optional **
#    """
#    name = models.CharField(
#                            null = False,
#                            blank = False,
#                            max_length = 255,
#                            db_index = True,
#                            verbose_name = "Name",
#                            help_text = "Name of the map save",
#                            )
#    desc = models.TextField(
#                            null = False,
#                            blank = True,
#                            default = '',
#                            verbose_name = "Description of the map save",
#                            )
#    version = models.CharField(
#                            null = False,
#                            blank = False,
#                            max_length = 255,
#                            db_index = True,
#                            verbose_name = "Version",
#                            help_text = "Version of the map save",
#                            )
#    owners = models.ForeignKey(
#                              User,
#                              null = False,
#                              editable = False,
#                              verbose_name = "Owner",
#                              )
#    zipName = models.CharField(
#                            null = False,
#                            blank = False,
#                            max_length = 255,
#                            db_index = True,
#                            verbose_name = "Map ZIP Name",
#                            help_text = "Name of the map save's ZIP file",
#                            )
#    created = models.DateTimeField(
#                                    null = False,
#                                    auto_now_add = True,
#                                    editable = False,
#                                    verbose_name = "Date Created",
#                                    help_text = "The date that this map save was created",
#                                    )
#    modified = models.DateTimeField(
#                                    null = False,
#                                    auto_now = True,
#                                    editable = False,
#                                    verbose_name = "Date Modified",
#                                    help_text = "The date that this map save object was last modified",
#                                    )
# admin.site.register(PublicMapSave)


class MapSave(models.Model):
    """ Allow users to save maps. 
    Note: Map files are NOT private. 
    Note: The zip must be in the following structure
        /world/<map data>
        /world_nether/<map data>         ** optional **
        /world_the_end/<map data>         ** optional **
    """
    name = models.SlugField(
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Name",
                            help_text = "Name of the map save",
                            )
    desc = models.TextField(
                            null = False,
                            blank = True,
                            default = '',
                            verbose_name = "Description of the map save",
                            )
    version = models.CharField(
                            null = False,
                            blank = True,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Version",
                            help_text = "Map version identifier for this save",
                            )
    owners = models.ForeignKey(
                              Group,
                              verbose_name = "Owners",
                              )
    zip = models.FileField(
                           null = False,
                           blank = False,
                           max_length = 4096,
                           upload_to = "maps/%Y/%m/%d/",
                           verbose_name = "Map File(s)",
                           help_text = "A zip of the map directory(s)",
                           )
#    zipPW = models.CharField(
#                             null = False,
#                             blank = False,
#                             default = lambda: User.objects.make_random_password(length = 30, allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'),
#                             max_length = 255,
#                             verbose_name = "ZIP Password",
#                             help_text = "The password the ZIP file was encrypted with",
#                             )
    created = models.DateTimeField(
                                    null = False,
                                    auto_now_add = True,
                                    editable = False,
                                    verbose_name = "Date Created",
                                    help_text = "The date that this map save was created",
                                    )
    modified = models.DateTimeField(
                                    null = False,
                                    auto_now = True,
                                    editable = False,
                                    verbose_name = "Date Modified",
                                    help_text = "The date that this map save object was last modified",
                                    )
admin.site.register(MapSave)

class MinecraftServerCfgFile(models.Model):
    """ A config file for a minecraft server. 
    WARNING: Files listed here may be modified by the Minecraft Server proc. 
    """
    cfgLoc = models.CharField(
                              null = False,
                              blank = False,
                              db_index = True,
                              max_length = 255,
                              verbose_name = "File Location",
                              help_text = "The path to the file relative to the server home. Must be in the server type's CONFIG_FILES list. ",
                              )
    serverInstance = models.ForeignKey(
                                       MinecraftServer,
                                       db_index = True,
                                       verbose_name = "Server Binary",
                                       help_text = "The type/version of server to run",
                                       )
admin.site.register(MinecraftServerCfgFile)
