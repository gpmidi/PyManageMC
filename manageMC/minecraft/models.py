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
# Built-in
import os.path  # @UnusedImport
import json

# Django
from django.db import models  # @UnusedImport
from django.contrib.auth.models import User, Group  # @UnusedImport
from django.conf import settings  # @UnusedImport
from django.core.validators import MinLengthValidator, MaxValueValidator  # @UnusedImport
from django.core.validators import validate_slug, MinValueValidator  # @UnusedImport
from django.core.cache import get_cache  # @UnusedImport

# CouchDB
from couchdbkit.ext.django.schema import *  # @UnusedWildImport
from couchdbkit.exceptions import ResourceNotFound  # @UnusedImport

# Load serverType objects
from minecraft.serverType import loadOtherServerTypes, allServerTypes  # @UnusedImport
from minecraft.validators import *  # @UnusedWildImport
from mcdocker.models import *  # @UnusedWildImport

# Ours
from mcprofile import MinecraftUser


class MinecraftServerBinary(Document):
    # TODO: Move this to a doc
    TYPE_NAME_CHOICES = (
                          # (TYPE string, human name),
                          ('Stock', 'Stock'),
                          ('Bukkit', 'Bukkit'),
                          ('Tekkit', 'Tekkit'),
                          ('NerdBukkit', 'NerdBukkit'),
                          ('FTB', "Feed The Beast"),
                         )
    typeName = StringProperty(
                              required=True,
                              default=None,
                              validators=[],
                              name="typeName",
                              verbose_name="Name of the server type",
                              choices=TYPE_NAME_CHOICES,
                              )
    version = StringProperty(
                              required=True,
                              default=None,
                              validators=[],
                              name="version",
                              verbose_name="Version of the binary",
                              )
    RELEASE_STATUS_CHOICES = (
                          # (TYPE string, human name),
                          ('Production Release', 'Production Release'),
                          ('Dev Build', 'Dev Build'),
                          ('Mature Release', 'Mature Release'),
                          ('Nightly Dev Build', 'Nightly Dev Build'),
                          ('Pre-release', 'Pre-release'),
                          ('Beta', 'Beta'),
                          ('Alpha', 'Alpha'),
                          )
    releaseStatus = StringProperty(
                              required=True,
                              default=None,
                              validators=[],
                              name="releaseStatus",
                              verbose_name="Name of the server type",
                              choices=RELEASE_STATUS_CHOICES,
                              )
    created = DateTimeProperty(
                                # default=
                                required=True,
                                validators=[],
                                name="created",
                                auto_now_add=True,
                                verbose_name="The date that this server bin was first defined",
                                )
    modified = DateTimeProperty(
                                # default=
                                required=True,
                                validators=[],
                                name="modified",
                                auto_now=True,
                                verbose_name="The date that this server bin was last modified",
                                )

    def __str__(self):
        return "%s Minecraft Server Version %s" % (self.typeName, self.version)

    def __repr__(self):
        return "<MCServerBin_%s_%s>" % (self.typeName, self.version)


class MinecraftServer(Document):
    name = StringProperty(
                          validators=[validate_serverInstance, ],
                          name="MinecraftServer",
                          required=True,
                          default=None,
                          verbose_name="Server Instance",
                          )
    # User friendly info
    humanName = StringProperty(
                          validators=[],
                          name="humanName",
                          required=True,
                          default=None,
                          verbose_name="Image Name",
                          )
    description = StringProperty(
                          validators=[],
                          name="humanDescription",
                          required=True,
                          default='',
                          verbose_name="Image Description",
                          )

    def getSplitDescription(self):
        """ Return description as list of lines without trailing newlines """
        return map(lambda x: x.rstrip(), str(self.description).splitlines())

    binary = StringProperty(
                              required=True,
                              default=None,
                              validators=[validate_serverBinary, ],
                              name="Binary",
                              verbose_name="MinecraftServerBinary of the binary",
                              )
    # Docker image
    image = StringProperty(
                          required=True,
                          default=None,
                          validators=[validate_serverImage, ],
                          name="Image",
                          verbose_name="OS Image",
                          )
    # An actual running docker image
    container = StringProperty(
                          required=False,
                          default=None,
                          validators=[RegexValidator(r'^[a-f0-9]+$'), ],  # TODO: Add container name validator
                          name="Container",
                          verbose_name="OS Instance",
                          )
    created = DateTimeProperty(
                                # default=
                                required=True,
                                validators=[],
                                name="Date Created",
                                auto_now_add=True,
                                verbose_name="The date that this server bin was first defined",
                                )
    modified = DateTimeProperty(
                                # default=
                                required=True,
                                validators=[],
                                name="Date Modified",
                                auto_now=True,
                                verbose_name="The date that this server bin was last modified",
                                )

    def __str__(self):
        return "MCServer_%s_%s" % (self.name, self.getSessionName())

    def __repr__(self):
        return "<MCServer %r %r>" % (self.name, self.getSessionName())

    def getSessionName(self):
        """ Returns the screen session name.
        Must NEVER change.
        """
        return "MC-%s" % self.name

    @classmethod
    def makeSessionName(cls, name):
        """ Returns the screen session name.
        Must NEVER change.
        """
        return "MC-%s" % name

    def getInstance(self):
        """ Returns the minecraft server object for hosted instances
        or None if it is not hosted """
        try:
            return ServerInstance.objects.get(pk=self.name)
        except ServerInstance.DoesNotExist:
            return None

    def getImage(self):
        try:
            return DockerImage.get(self.image)
        except ResourceNotFound:
            return None

    def getVolumeLocation(self, volumeName):
        """
        @return: <path inside docker instance>
        """
        assert volumeName in self.getImage().volumes
        return self.getImage().volumes[volumeName]

    def getVolumeLocations(self):
        """
        @return: { <volume type name>:<path inside docker instance>,}
        """
        ret = {}
        for name, intPath in self.getImage().volumes.items():
            ret[self.getVolumeLocation(volumeName=name)] = intPath
        return ret


# class MinecraftServerBinary(models.Model):
#     """ A type of Minecraft server a a specific version """
#     typeName = models.CharField(
#                                 null = False,
#                                 blank = False,
#                                 max_length = 255,
#                                 db_index = True,
#                                 verbose_name = "Name",
#                                 help_text = "Name of the server type",
#                                 choices = (
#                                               # (TYPE string, human name),
#                                               ('Stock', 'Stock'),
#                                               ('Bukkit', 'Bukkit'),
#                                               ('Tekkit', 'Tekkit'),
#                                               ('NerdBukkit', 'NerdBukkit'),
#                                               ('FTB', "Feed The Beast"),
#                                            ),
#                                 )
#     exc = models.FileField(
#                            null = True,
#                            blank = False,
#                            max_length = 4096,
#                            upload_to = "srv/jars/%Y/%m/%d/",
#                            verbose_name = "Exec",
#                            help_text = "The binary JAR file",
#                            )
#     files = models.FileField(
#                                null = True,
#                                blank = True,
#                                max_length = 4096,
#                                upload_to = "srv/files/%Y/%m/%d/",
#                                verbose_name = "Support Files - Overwrite",
#                                help_text = "A ZIP file containing any supporting files. Will overwrite any existing files with the same name/path. ",
#                                )
#     version = models.CharField(
#                             null = False,
#                             blank = False,
#                             max_length = 255,
#                             db_index = True,
#                             verbose_name = "Version",
#                             help_text = "Version of the binary",
#                             )
#     releaseStatus = models.CharField(
#                                 null = False,
#                                 blank = False,
#                                 max_length = 255,
#                                 verbose_name = "Release Status",
#                                 help_text = "This server version release type",
#                                 choices = (
#                                               # (TYPE string, human name),
#                                               ('Production Release', 'Production Release'),
#                                               ('Dev Build', 'Dev Build'),
#                                               ('Mature Release', 'Mature Release'),
#                                               ('Nightly Dev Build', 'Nightly Dev Build'),
#                                               ('Pre-release', 'Pre-release'),
#                                               ('Beta', 'Beta'),
#                                               ('Alpha', 'Alpha'),
#                                            ),
#                                 )
#     created = models.DateTimeField(
#                                     null = False,
#                                     auto_now_add = True,
#                                     editable = False,
#                                     verbose_name = "Date Created",
#                                     help_text = "The date that this server bin was first defined",
#                                     )
#     modified = models.DateTimeField(
#                                     null = False,
#                                     auto_now = True,
#                                     editable = False,
#                                     verbose_name = "Date Modified",
#                                     help_text = "The date that this server bin was last modified",
#                                     )
#
#     def __str__(self):
#         return "MCServerBin %s_%s" % (self.typeName, self.version)
#
#     def __repr__(self):
#         return "<MCServerBin_%s_%s>" % (self.typeName, self.version)


# class MinecraftServer(models.Model):
#     """ A standard Minecraft server """
#     name = models.CharField(
#                             null = False,
#                             blank = False,
#                             max_length = 255,
#                             db_index = True,
#                             editable = True,
#                             verbose_name = "Name",
#                             help_text = "Name of this server",
#                             )
#     bin = models.ForeignKey(
#                              MinecraftServerBinary,
#                              db_index = True,
#                              verbose_name = "Server Binary",
#                              help_text = "The type/version of server to run",
#                              )
#     created = models.DateTimeField(
#                                     null = False,
#                                     auto_now_add = True,
#                                     editable = False,
#                                     verbose_name = "Date Created",
#                                     help_text = "The date that this server was created",
#                                     )
#     modified = models.DateTimeField(
#                                     null = False,
#                                     auto_now = True,
#                                     editable = False,
#                                     verbose_name = "Date Modified",
#                                     help_text = "The date that this server object was last modified",
#                                     )
#     instance = models.OneToOneField(
#                                     'extern.ServerInstance',
#                                     null = False,
#                                     db_index = True,
#                                     editable = False,
#                                     verbose_name = "Server Instance",
#                                     # help_text="",
#                                     )
#
#     def __str__(self):
#         return "MCServer_%s_%s" % (self.name, self.getSessionName())
#
#     def __repr__(self):
#         return "<MCServer %r %r>" % (self.name, self.getSessionName())
#
#     def loc(self):
#         """ Return the full path to the server """
#         return os.path.join(settings.MC_SERVER_PATH, str(self.getSessionName()))
#
#     def getSessionName(self):
#         """ Returns the screen session name.
#         Must NEVER change.
#         """
#         return "MC-%d" % self.pk


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


class MapSave(Document):
    """ A Minecraft server config file
    """
    name = StringProperty(
                           verbose_name="Name of the map save",
                           default=None,
                           required=True,
                           )
    desc = StringProperty(
                           verbose_name="Description of the map save",
                           default='',
                           required=False,
                           )
    version = StringProperty(
                             verbose_name="User defined map version identifier for this save",
                             default='',
                             required=False,
                             )
    owners = StringProperty(
                            verbose_name="Map Owners",
                            default=None,
                            required=True,
                            )

    # When
    created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )


# class MapSave(models.Model):
#     """ Allow users to save maps.
#     Note: Map files are NOT private.
#     Note: The zip must be in the following structure
#         /world/<map data>
#         /world_nether/<map data>         ** optional **
#         /world_the_end/<map data>         ** optional **
#     """
#     name = models.SlugField(
#                             null = False,
#                             blank = False,
#                             max_length = 255,
#                             db_index = True,
#                             verbose_name = "Name",
#                             help_text = "Name of the map save",
#                             validators = [ validate_slug, ],
#                             )
#     desc = models.TextField(
#                             null = False,
#                             blank = True,
#                             default = '',
#                             verbose_name = "Description of the map save
#                             )
#     version = models.CharField(
#                             null = False,
#                             blank = True,
#                             max_length = 255,
#                             db_index = True,
#                             verbose_name = "Version",
#                             help_text = "Map version identifier for this save",
#                             )
#     owners = models.ForeignKey(
#                               Group,
#                               verbose_name = "Owners",
#                               null = True,
#                               blank = False,
#                               )
#     zip = models.FileField(
#                            null = False,
#                            blank = False,
#                            max_length = 4096,
#                            upload_to = "maps/%Y/%m/%d/",
#                            verbose_name = "Map File(s)",
#                            help_text = "A zip of the map directory(s)",
#                            )
# #    zipPW = models.CharField(
# #                             null = False,
# #                             blank = False,
# #                             default = lambda: User.objects.make_random_password(length = 30, allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'),
# #                             max_length = 255,
# #                             verbose_name = "ZIP Password",
# #                             help_text = "The password the ZIP file was encrypted with",
# #                             )
#     created = models.DateTimeField(
#                                     null = False,
#                                     auto_now_add = True,
#                                     editable = False,
#                                     verbose_name = "Date Created",
#                                     help_text = "The date that this map save was created",
#                                     )
#     modified = models.DateTimeField(
#                                     null = False,
#                                     auto_now = True,
#                                     editable = False,
#                                     verbose_name = "Date Modified",
#                                     help_text = "The date that this map save object was last modified",
#                                     )

# # FIXME: Can this be removed?
# class MinecraftServerCfgFile(models.Model):
#     """ A config file for a minecraft server.
#     WARNING: Files listed here may be modified by the Minecraft Server proc.
#     """
#     cfgLoc = models.CharField(
#                               null = False,
#                               blank = False,
#                               db_index = True,
#                               max_length = 255,
#                               verbose_name = "File Location",
#                               help_text = "The path to the file relative to the server home. Must be in the server type's CONFIG_FILES list. ",
#                               )
#     serverInstance = models.ForeignKey(
#                                        MinecraftServer,
#                                        db_index = True,
#                                        verbose_name = "Server Binary",
#                                        help_text = "The type/version of server to run",
#                                        )


class BannedIPConfig(DocumentSchema):
    """
  {
    "ip": "1.2.3.4",
    "created": "2014-04-09 22:43:45 -0400",
    "source": "(Unknown)",
    "expires": "forever",
    "reason": "Banned by an operator."
  }
    """
    ip = StringProperty(
                    verbose_name='Reason',
                    default=None,
                    required=True,
                    name='ip',
                    )
    created = StringProperty(
                    verbose_name='Reason',
                    required=True,
                    name='created',
                    )
    source = StringProperty(
                    verbose_name='Reason',
                    default='(Unknown)',
                    required=True,
                    name='source',
                    )
    expires = StringProperty(
                    verbose_name='Reason',
                    default='forever',
                    required=True,
                    name='expires',
                    )
    reason = StringProperty(
                    verbose_name='Reason',
                    default='Banned by an operator.',
                    required=True,
                    name='reason',
                    )

class BannedIPsConfig(Document):
    """ A Minecraft server banned IPs
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='BannedIPsConfigFileType',
                                        required=True,
                                        )

    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )
    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default='banned-ips.json',
                                required=False,
                                )
    banned = SchemaListProperty(
                                BannedIPConfig,
                                verbose_name="Banned IPs",
                                default=[],
                                required=True,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment('banned-ips.json', stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='banned-ips.json',
                                )

    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment('banned-ips.json.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='banned-ips.json.old',
                                )


class BannedPlayerConfig(DocumentSchema):
    """
  {
    "uuid": "8b489868-248c-4744-a32d-021f0d7f7f50",
    "name": "abc12345",
    "created": "2014-04-09 22:43:44 -0400",
    "source": "(Unknown)",
    "expires": "forever",
    "reason": "Banned by an operator."
  },

    """
    name = StringProperty(
                    verbose_name='Username',
                    default=None,
                    required=True,
                    name='name',
                    )
    uuid = StringProperty(
                    verbose_name='UUID',
                    default=None,
                    required=True,
                    name='uuid',
                    )
    created = StringProperty(
                    verbose_name='Reason',
                    required=True,
                    name='created',
                    )
    source = StringProperty(
                    verbose_name='Reason',
                    default='(Unknown)',
                    required=True,
                    name='source',
                    )
    expires = StringProperty(
                    verbose_name='Reason',
                    default='forever',
                    required=True,
                    name='expires',
                    )
    reason = StringProperty(
                    verbose_name='Reason',
                    default='Banned by an operator.',
                    required=True,
                    name='reason',
                    )


class BannedPlayersConfig(Document):
    """ A Minecraft server banned players
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='BannedPlayersConfigFileType',
                                        required=True,
                                        )

    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )
    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default='banned-players.json',
                                required=False,
                                )
    banned = SchemaListProperty(
                                BannedPlayerConfig,
                                verbose_name="Banned Players",
                                default=[],
                                required=True,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment('banned-players.json', stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='banned-players.json',
                                )

    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment('banned-players.json.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='banned-players.json.old',
                                )


class OpConfig(DocumentSchema):
    """
  {
    "uuid": "85ff1e2c-3fc2-4640-a74f-2c24a834f285",
    "name": "abc123",
    "level": 3
  }
    """
    name = StringProperty(
                    verbose_name='Username',
                    default=None,
                    required=True,
                    name='name',
                    )
    uuid = StringProperty(
                    verbose_name='UUID',
                    default=None,
                    required=True,
                    name='uuid',
                    )
    level = IntegerProperty(
                            verbose_name='Level',
                            default=3,
                            required=True,
                            name='level'
                            )


class OpsConfig(Document):
    """ A Minecraft server Op players
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='OpsConfigFileType',
                                        required=True,
                                        )

    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )
    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default='ops.json',
                                required=False,
                                )
    oplist = SchemaListProperty(
                                OpConfig,
                                verbose_name="Op'ed Players",
                                default=[],
                                required=True,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment('ops.json', stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='ops.json',
                                )

    # Not using revisions because this guarantees availability of it
    # and because it's useful for change management
    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment('ops.json.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='ops.json.old',
                                )


class WhitelistUserConfig(DocumentSchema):
    """
  {
    "uuid": "178818cd-2f9f-46e8-add5-1cfd1e19f0f1",
    "name": "bcd2134"
  },
    """
    name = StringProperty(
                    verbose_name='Username',
                    default=None,
                    required=True,
                    name='name',
                    )
    uuid = StringProperty(
                    verbose_name='UUID',
                    default=None,
                    required=True,
                    name='uuid',
                    )


class WhitelistConfig(Document):
    """ A Minecraft server's whitelisted players
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='WhiteListConfigFileType',
                                        required=True,
                                        )

    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )
    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default='whitelist.json',
                                required=False,
                                )
    users = SchemaListProperty(
                                WhitelistUserConfig,
                                verbose_name="Whitelisted Players",
                                default=[],
                                required=True,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment('whitelist.json', stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='whitelist.json',
                                )

    # Not using revisions because this guarantees availability of it
    # and because it's useful for change management
    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment('whitelist.json.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='whitelist.json.old',
                                )


class UserCacheConfig(DocumentSchema):
    """
 {u'expiresOn': u'2014-05-09 22:43:45 -0400',
  u'name': u'Evangelion1990',
  u'uuid': u'cab6dbc0-130b-4da6-8e35-28f83935ddad'
 },
    """
    name = StringProperty(
                    verbose_name='Username',
                    default=None,
                    required=True,
                    name='name',
                    )
    uuid = StringProperty(
                    verbose_name='UUID',
                    default=None,
                    required=True,
                    name='uuid',
                    )
    expiresOn = StringProperty(
                    verbose_name='Expires On',
                    default=None,
                    required=True,
                    name='expiresOn',
                    )


class UsersCacheConfig(Document):
    """ A Minecraft server players cache
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='UsersCacheConfigFileType',
                                        required=True,
                                        )

    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )
    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default='usercache.json',
                                required=False,
                                )
    users = SchemaListProperty(
                                UserCacheConfig,
                                verbose_name="Cached Players",
                                default=[],
                                required=True,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment('usercache.json', stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='usercache.json',
                                )

    # Not using revisions because this guarantees availability of it
    # and because it's useful for change management
    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment('usercache.json.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='usercache.json.old',
                                )


class MinecraftServerProperties(Document):
    """ A Minecraft server config file
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    # @warning: All options that are not server.properties keys MUST be prefixed with "nc_".
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='ServerProperitiesConfigFileType',
                                        required=True,
                                        )
    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )
    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    # File attrs
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )
    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default='server.properties',
                                required=False,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment('server.properties', stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        # FIXME: Add in code to move existing to previous config file(s) and or file hash
        return self.put_attachment(
                                content=str(data),
                                name='server.properties',
                                )

    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment('server.properties.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name='server.properties.old',
                                )

    # ## Ones that are important


    # ## Below are auto-generated attrs

    # This is the message that is displayed in the server list of the client, below the name.
    # MC Default: ''A Minecraft Server''
    motd = StringProperty(
            verbose_name='motd',
            name='motd',
            default="Welcome to Minecraft!",
            required=True,
            )

    # Enable PvP on the server. Players shooting themselves with arrows will only receive damage if PvP is enabled.
    # MC Default: true
    pvp = BooleanProperty(
            verbose_name='pvp',
            name='pvp',
            default=None,
            required=False,
            )

    # Allows players to travel to the [[Nether]].
    # MC Default: true
    allow_nether = BooleanProperty(
            verbose_name='allow-nether',
            name='allow-nether',
            default=None,
            required=False,
            )

    # The maximum number of players that can play on the server at the same time. Note that if more players are on the server it will use more resources.  Note also, op player connections are not supposed to count against the max players, but ops currently cannot join a full server. Extremely large values for this field result in the client-side user list being broken.
    # MC Default: 20
    max_players = IntegerProperty(
            verbose_name='max-players',
            name='max-players',
            default=None,
            required=False,
            )

    # Sets permission level for ops.
    # MC Default: 4
    op_permission_level = IntegerProperty(
            verbose_name='op-permission-level',
            name='op-permission-level',
            default=None,
            required=False,
            )

    # Sets whether the server sends snoop data regularly to http://snoop.minecraft.net.
    # MC Default: true
    snooper_enabled = BooleanProperty(
            verbose_name='snooper-enabled',
            name='snooper-enabled',
            default=None,
            required=False,
            )

    # Defines the mode of gameplay.
    # MC Default: 0
    gamemode = IntegerProperty(
            verbose_name='gamemode',
            name='gamemode',
            default=None,
            required=False,
            )

    # Determines if [[animals]] will be able to spawn.
    # MC Default: true
    spawn_animals = BooleanProperty(
            verbose_name='spawn-animals',
            name='spawn-animals',
            default=None,
            required=False,
            )

    # The settings used to customize Superflat world generation.  See [[Superflat]] for possible settings and examples.
    # MC Default: ''blank''
    generator_settings = StringProperty(
            verbose_name='generator-settings',
            name='generator-settings',
            default=None,
            required=False,
            )

    # Changes the port the server is hosting (listening) on. This port must be [http://en.wikipedia.org/wiki/Port_forwarding forwarded] if the server is hosted in a network using [http://en.wikipedia.org/wiki/Network_address_translation NAT] (If you have a home router/firewall).
    # MC Default: 25565
    server_port = IntegerProperty(
            verbose_name='server-port',
            name='server-port',
            default=None,
            required=False,
            )

    # Enables GameSpy4 protocol server listener. Used to get information about server.
    # MC Default: false
    enable_query = BooleanProperty(
            verbose_name='enable-query',
            name='enable-query',
            default=None,
            required=False,
            )

    # Server prompts client to download texture pack upon join. This link '''must''' be a direct link to the actual texture pack .zip file. High-resolution texture packs must be less than or equal to 10,000,000 bytes (approx 9.54MB) in size.
    # MC Default: ''blank''
    texture_pack = StringProperty(
            verbose_name='texture-pack',
            name='texture-pack',
            default=None,
            required=False,
            )

    # Sets the port for the query server (see '''enable-query''').
    # MC Default: 25565
    query_port = IntegerProperty(
            verbose_name='query.port',
            name='query.port',
            default=None,
            required=False,
            )

    # Sets the port to rcon.
    # MC Default: 25575
    rcon_port = IntegerProperty(
            verbose_name='rcon.port',
            name='rcon.port',
            default=None,
            required=False,
            )

    # Determines the radius of the spawn protection.  Setting this to 0 will not disable spawn protection.  0 will protect the single block at the spawn point.  1 will protect a 3x3 area centered on the spawn point.  2 will protect 5x5, 3 will protect 7x7, etc. This option is not generated on the first server start and appears when the first player joins.  If there are no [[Operator|ops]] set on the server, the spawn protection will be disabled automatically.
    # MC Default: 16
    spawn_protection = IntegerProperty(
            verbose_name='spawn-protection',
            name='spawn-protection',
            default=None,
            required=False,
            )

    # Determines the type of map that is generated.
    # MC Default: DEFAULT
    level_type = StringProperty(
            verbose_name='level-type',
            name='level-type',
            default=None,
            required=False,
            )

    # Defines whether [[structures]] (such as villages) will be generated.
    # MC Default: true
    generate_structures = BooleanProperty(
            verbose_name='generate-structures',
            name='generate-structures',
            default=None,
            required=False,
            )

    # Defines the [[difficulty]] (such as damage dealt by mobs and the way hunger and poison affects players) of the server.
    # MC Default: 1
    difficulty = IntegerProperty(
            verbose_name='difficulty',
            name='difficulty',
            default=None,
            required=False,
            )

    # Sets the password to rcon.
    # MC Default: ''blank''
    rcon_password = StringProperty(
            verbose_name='rcon.password',
            name='rcon.password',
            default=None,
            required=False,
            )

    # Sets the amount of world data the server sends the client, measured in chunks in each direction of the player (radius, not diameter). It determines the server-side viewing distance. The "Far" viewing distance is 16 chunks, sending 1089 total chunks (the amount of chunks that the server will load can be seen in the [[debug screen]]). "Normal" view distance is 8, for 289 chunks.
    # MC Default: 10
    view_distance = IntegerProperty(
            verbose_name='view-distance',
            name='view-distance',
            default=None,
            required=False,
            )

    # If set to '''true''', <!-- Server difficulty set to hard and difficulty setting ignored? -->players will be permanently banned<!-- verify --> if they die.
    # MC Default: false
    hardcore = BooleanProperty(
            verbose_name='hardcore',
            name='hardcore',
            default=None,
            required=False,
            )

    # Allows users to use flight on your server while in Survival mode, if they have a [[mod]] that provides flight installed.
    # MC Default: false
    allow_flight = BooleanProperty(
            verbose_name='allow-flight',
            name='allow-flight',
            default=None,
            required=False,
            )

    # Server checks connecting players against minecraft's account database. Only set this to false if your server is '''not''' connected to the Internet. Hackers with fake accounts can connect if this is set to false! If minecraft.net is down or inaccessible, no players will be able to connect if this is set to true. Setting this variable to off purposely is called "cracking" a server, and servers that are presently with online mode off are called "cracked" servers.
    # MC Default: true
    online_mode = BooleanProperty(
            verbose_name='online-mode',
            name='online-mode',
            default=None,
            required=False,
            )

    # Determines if monsters will be spawned.
    # MC Default: true
    spawn_monsters = BooleanProperty(
            verbose_name='spawn-monsters',
            name='spawn-monsters',
            default=None,
            required=False,
            )

    # Force players to join in the default gamemode.
    # MC Default: false
    force_gamemode = BooleanProperty(
            verbose_name='force-gamemode',
            name='force-gamemode',
            default=None,
            required=False,
            )

    # Determines if villagers will be spawned.
    # MC Default: true
    spawn_npcs = BooleanProperty(
            verbose_name='spawn-npcs',
            name='spawn-npcs',
            default=None,
            required=False,
            )

    # Enables command blocks
    # MC Default: false
    enable_command_block = BooleanProperty(
            verbose_name='enable-command-block',
            name='enable-command-block',
            default=None,
            required=False,
            )

    # Enables a whitelist on the server.
    # MC Default: false
    white_list = BooleanProperty(
            verbose_name='white-list',
            name='white-list',
            default=None,
            required=False,
            )

    # Enables remote access to the server console.
    # MC Default: false
    enable_rcon = BooleanProperty(
            verbose_name='enable-rcon',
            name='enable-rcon',
            default=None,
            required=False,
            )

    # The "level-name" value will be used as the world name and its folder name. You may also copy your saved game folder here, and change the name to the same as that folder's to load it instead.
    # MC Default: world
    level_name = StringProperty(
            verbose_name='level-name',
            name='level-name',
            default=None,
            required=False,
            )

    # The maximum height in which building is allowed. Terrain may still naturally generate above a low height limit.
    # MC Default: 256
    max_build_height = IntegerProperty(
            verbose_name='max-build-height',
            name='max-build-height',
            default=None,
            required=False,
            )

    # Set this if you want the server to bind to a particular IP.  It is strongly recommended that you leave server-ip blank!
    # MC Default: ''blank''
    server_ip = StringProperty(
            verbose_name='server-ip',
            name='server-ip',
            default=None,
            required=False,
            )

    # Add a [[Seed (Level Generation)|seed]] for your world, as in Singleplayer.
    # MC Default: ''blank''
    level_seed = StringProperty(
            verbose_name='level-seed',
            name='level-seed',
            default=None,
            required=False,
            )


class GenericConfig(Document):
    """ A generic config file for a Minecraft server
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    nc_configFileTypeName = StringProperty(
                                        verbose_name='Config File Type Name',
                                        default='ConfigFileType',
                                        required=True,
                                        )

    nc_minecraftServerPK = StringProperty(
                                        verbose_name='MinecraftServer\'s PK',
                                        required=True,
                                        validators=[validate_serverInstance, ],
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name="Date Created",
                               required=True,
                               auto_now_add=True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name="Date Modified",
                               required=False,
                               default=None,
                               auto_now=True,
                               )
    nc_lastHash = StringProperty(
                                verbose_name="Last Hash",
                                default=None,
                                required=False,
                                )

    nc_fileName = StringProperty(
                                verbose_name="File Name & Path",
                                default=None,
                                required=False,
                                )

    def getConfigFile(self):
        try:
            return str(self.fetch_attachment(self.fileName, stream=False))
        except Exception as e:
            return None

    def putConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name=self.fileName,
                                )

    def getLastConfigFile(self):
        try:
            return str(self.fetch_attachment(self.fileName + '.old', stream=False))
        except Exception as e:
            return None

    def putLastConfigFile(self, data):
        return self.put_attachment(
                                content=str(data),
                                name=self.fileName + '.old',
                                )

