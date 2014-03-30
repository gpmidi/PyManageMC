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
import os.path

# Django
from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.validators import MinLengthValidator, MaxValueValidator
from django.core.validators import validate_slug, MinValueValidator

# CouchDB
from couchdbkit.ext.django.schema import *

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
        return "MCServerBin %s_%s" % (self.typeName, self.version)
    
    def __repr__(self):
        return "<MCServerBin_%s_%s>" % (self.typeName, self.version)
    

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
                            validators = [ validate_slug, ],
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
                              null = True,
                              blank = False,
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

# FIXME: Can this be removed?
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


class MinecraftServerProperties(Document):
    """ A Minecraft server config file
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used for a record given the server info """
        from minecraft.serverType import ServerProperitiesConfigFileType
        # FIXME: Should 'cls' be 'ServerProperitiesConfigFileType'?
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    # @warning: All options that are not server.properties keys MUST be prefixed with "nc_".
    nc_configFileTypeName = StringProperty(
                                        verbose_name = 'Config File Type Name',
                                        default = 'ServerProperitiesConfigFileType',
                                        required = True,
                                        )

    nc_minecraftServerPK = IntegerProperty(
                                        verbose_name = 'MinecraftServer\'s PK',
                                        required = True,
                                        )

    # When
    nc_created = DateTimeProperty(
                               verbose_name = "Date Created",
                               required = True,
                               auto_now_add = True,
                               )
    nc_modified = DateTimeProperty(
                               verbose_name = "Date Modified",
                               required = False,
                               default = None,
                               auto_now = True,
                               )


    # ## Ones that are important


    # ## Below are auto-generated attrs

    # This is the message that is displayed in the server list of the client, below the name.
    # MC Default: ''A Minecraft Server''
    motd = StringProperty(
            verbose_name = 'motd',
            name = 'motd',
            default = "Welcome to Minecraft!",
            required = True,
            )

    # Enable PvP on the server. Players shooting themselves with arrows will only receive damage if PvP is enabled.
    # MC Default: true
    pvp = BooleanProperty(
            verbose_name = 'pvp',
            name = 'pvp',
            default = None,
            required = False,
            )

    # Allows players to travel to the [[Nether]].
    # MC Default: true
    allow_nether = BooleanProperty(
            verbose_name = 'allow-nether',
            name = 'allow-nether',
            default = None,
            required = False,
            )

    # The maximum number of players that can play on the server at the same time. Note that if more players are on the server it will use more resources.  Note also, op player connections are not supposed to count against the max players, but ops currently cannot join a full server. Extremely large values for this field result in the client-side user list being broken.
    # MC Default: 20
    max_players = IntegerProperty(
            verbose_name = 'max-players',
            name = 'max-players',
            default = None,
            required = False,
            )

    # Sets permission level for ops.
    # MC Default: 4
    op_permission_level = IntegerProperty(
            verbose_name = 'op-permission-level',
            name = 'op-permission-level',
            default = None,
            required = False,
            )

    # Sets whether the server sends snoop data regularly to http://snoop.minecraft.net.
    # MC Default: true
    snooper_enabled = BooleanProperty(
            verbose_name = 'snooper-enabled',
            name = 'snooper-enabled',
            default = None,
            required = False,
            )

    # Defines the mode of gameplay.
    # MC Default: 0
    gamemode = IntegerProperty(
            verbose_name = 'gamemode',
            name = 'gamemode',
            default = None,
            required = False,
            )

    # Determines if [[animals]] will be able to spawn.
    # MC Default: true
    spawn_animals = BooleanProperty(
            verbose_name = 'spawn-animals',
            name = 'spawn-animals',
            default = None,
            required = False,
            )

    # The settings used to customize Superflat world generation.  See [[Superflat]] for possible settings and examples.
    # MC Default: ''blank''
    generator_settings = StringProperty(
            verbose_name = 'generator-settings',
            name = 'generator-settings',
            default = None,
            required = False,
            )

    # Changes the port the server is hosting (listening) on. This port must be [http://en.wikipedia.org/wiki/Port_forwarding forwarded] if the server is hosted in a network using [http://en.wikipedia.org/wiki/Network_address_translation NAT] (If you have a home router/firewall).
    # MC Default: 25565
    server_port = IntegerProperty(
            verbose_name = 'server-port',
            name = 'server-port',
            default = None,
            required = False,
            )

    # Enables GameSpy4 protocol server listener. Used to get information about server.
    # MC Default: false
    enable_query = BooleanProperty(
            verbose_name = 'enable-query',
            name = 'enable-query',
            default = None,
            required = False,
            )

    # Server prompts client to download texture pack upon join. This link '''must''' be a direct link to the actual texture pack .zip file. High-resolution texture packs must be less than or equal to 10,000,000 bytes (approx 9.54MB) in size.
    # MC Default: ''blank''
    texture_pack = StringProperty(
            verbose_name = 'texture-pack',
            name = 'texture-pack',
            default = None,
            required = False,
            )

    # Sets the port for the query server (see '''enable-query''').
    # MC Default: 25565
    query_port = IntegerProperty(
            verbose_name = 'query.port',
            name = 'query.port',
            default = None,
            required = False,
            )

    # Sets the port to rcon.
    # MC Default: 25575
    rcon_port = IntegerProperty(
            verbose_name = 'rcon.port',
            name = 'rcon.port',
            default = None,
            required = False,
            )

    # Determines the radius of the spawn protection.  Setting this to 0 will not disable spawn protection.  0 will protect the single block at the spawn point.  1 will protect a 3x3 area centered on the spawn point.  2 will protect 5x5, 3 will protect 7x7, etc. This option is not generated on the first server start and appears when the first player joins.  If there are no [[Operator|ops]] set on the server, the spawn protection will be disabled automatically.
    # MC Default: 16
    spawn_protection = IntegerProperty(
            verbose_name = 'spawn-protection',
            name = 'spawn-protection',
            default = None,
            required = False,
            )

    # Determines the type of map that is generated.
    # MC Default: DEFAULT
    level_type = StringProperty(
            verbose_name = 'level-type',
            name = 'level-type',
            default = None,
            required = False,
            )

    # Defines whether [[structures]] (such as villages) will be generated.
    # MC Default: true
    generate_structures = BooleanProperty(
            verbose_name = 'generate-structures',
            name = 'generate-structures',
            default = None,
            required = False,
            )

    # Defines the [[difficulty]] (such as damage dealt by mobs and the way hunger and poison affects players) of the server.
    # MC Default: 1
    difficulty = IntegerProperty(
            verbose_name = 'difficulty',
            name = 'difficulty',
            default = None,
            required = False,
            )

    # Sets the password to rcon.
    # MC Default: ''blank''
    rcon_password = StringProperty(
            verbose_name = 'rcon.password',
            name = 'rcon.password',
            default = None,
            required = False,
            )

    # Sets the amount of world data the server sends the client, measured in chunks in each direction of the player (radius, not diameter). It determines the server-side viewing distance. The "Far" viewing distance is 16 chunks, sending 1089 total chunks (the amount of chunks that the server will load can be seen in the [[debug screen]]). "Normal" view distance is 8, for 289 chunks.
    # MC Default: 10
    view_distance = IntegerProperty(
            verbose_name = 'view-distance',
            name = 'view-distance',
            default = None,
            required = False,
            )

    # If set to '''true''', <!-- Server difficulty set to hard and difficulty setting ignored? -->players will be permanently banned<!-- verify --> if they die.
    # MC Default: false
    hardcore = BooleanProperty(
            verbose_name = 'hardcore',
            name = 'hardcore',
            default = None,
            required = False,
            )

    # Allows users to use flight on your server while in Survival mode, if they have a [[mod]] that provides flight installed.
    # MC Default: false
    allow_flight = BooleanProperty(
            verbose_name = 'allow-flight',
            name = 'allow-flight',
            default = None,
            required = False,
            )

    # Server checks connecting players against minecraft's account database. Only set this to false if your server is '''not''' connected to the Internet. Hackers with fake accounts can connect if this is set to false! If minecraft.net is down or inaccessible, no players will be able to connect if this is set to true. Setting this variable to off purposely is called "cracking" a server, and servers that are presently with online mode off are called "cracked" servers.
    # MC Default: true
    online_mode = BooleanProperty(
            verbose_name = 'online-mode',
            name = 'online-mode',
            default = None,
            required = False,
            )

    # Determines if monsters will be spawned.
    # MC Default: true
    spawn_monsters = BooleanProperty(
            verbose_name = 'spawn-monsters',
            name = 'spawn-monsters',
            default = None,
            required = False,
            )

    # Force players to join in the default gamemode.
    # MC Default: false
    force_gamemode = BooleanProperty(
            verbose_name = 'force-gamemode',
            name = 'force-gamemode',
            default = None,
            required = False,
            )

    # Determines if villagers will be spawned.
    # MC Default: true
    spawn_npcs = BooleanProperty(
            verbose_name = 'spawn-npcs',
            name = 'spawn-npcs',
            default = None,
            required = False,
            )

    # Enables command blocks
    # MC Default: false
    enable_command_block = BooleanProperty(
            verbose_name = 'enable-command-block',
            name = 'enable-command-block',
            default = None,
            required = False,
            )

    # Enables a whitelist on the server.
    # MC Default: false
    white_list = BooleanProperty(
            verbose_name = 'white-list',
            name = 'white-list',
            default = None,
            required = False,
            )

    # Enables remote access to the server console.
    # MC Default: false
    enable_rcon = BooleanProperty(
            verbose_name = 'enable-rcon',
            name = 'enable-rcon',
            default = None,
            required = False,
            )

    # The "level-name" value will be used as the world name and its folder name. You may also copy your saved game folder here, and change the name to the same as that folder's to load it instead.
    # MC Default: world
    level_name = StringProperty(
            verbose_name = 'level-name',
            name = 'level-name',
            default = None,
            required = False,
            )

    # The maximum height in which building is allowed. Terrain may still naturally generate above a low height limit.
    # MC Default: 256
    max_build_height = IntegerProperty(
            verbose_name = 'max-build-height',
            name = 'max-build-height',
            default = None,
            required = False,
            )

    # Set this if you want the server to bind to a particular IP.  It is strongly recommended that you leave server-ip blank!
    # MC Default: ''blank''
    server_ip = StringProperty(
            verbose_name = 'server-ip',
            name = 'server-ip',
            default = None,
            required = False,
            )

    # Add a [[Seed (Level Generation)|seed]] for your world, as in Singleplayer.
    # MC Default: ''blank''
    level_seed = StringProperty(
            verbose_name = 'level-seed',
            name = 'level-seed',
            default = None,
            required = False,
            )


class MinecraftServerLogLine(Document):
    """ A Minecraft server's log files
    """

    # When
    created = DateTimeProperty(
                               verbose_name = "Date Created",
                               required = True,
                               auto_now_add = True,
                               )
    logLine = StringProperty(
                             verbose_name = "Log Type",
                             required = True,
                             )


class MinecraftServerLogFile(DocumentSchema):
    """ One of a Minecraft server's log files 
    """
    # Standard In, Out, and Error
    LOGTYPE_STDIO = "stdio"
    # A on-disk log file
    LOGTYPE_FILE = "file"
    # Unknown
    LOGTYPE_UNK = "unknown"

    logType = StringProperty(
                             verbose_name = "Log Type",
                             default = LOGTYPE_UNK,
                             required = True,
                             choices = [
                                        LOGTYPE_STDIO,
                                        LOGTYPE_FILE,
                                        LOGTYPE_UNK,
                                        ],
                             )
    # A list of the keys of recent log lines
    rawLogLines = SchemaListProperty(
                                     MinecraftServerLogLine,
                                     verbose_name = "Raw Log Lines",
                                     required = True,
                                     default = [],
                                     )

    # When
    created = DateTimeProperty(
                               verbose_name = "Date Created",
                               required = True,
                               auto_now_add = True,
                               )
    modified = DateTimeProperty(
                               verbose_name = "Date Modified",
                               required = False,
                               default = None,
                               auto_now = True,
                               )

    # File Properties
    # None if not relevant for the given type of IO
    atime = DateTimeProperty(
                               verbose_name = "Date File Last Accessed",
                               required = True,
                               )
    ctime = DateTimeProperty(
                               verbose_name = "Date File Created",
                               required = True,
                               )
    mtime = DateTimeProperty(
                               verbose_name = "Date File Last Modified",
                               required = True,
                               )


class MinecraftServerLogs(Document):
    """ A Minecraft server's log files
    """

    @classmethod
    def makeServerID(cls, minecraftServerPK):
        """ Create the _id used  """
        # FIXME: Should 'cls' be 'ServerProperitiesConfigFileType'?
        return "%s-%s" % (cls.__name__, minecraftServerPK)

    # Standard Info
    logs = SchemaDictProperty(
                            MinecraftServerLogFile,
                            verbose_name = 'Config File Type Name',
                            default = 'ServerProperitiesConfigFileType',
                            required = False,
                            )

    minecraftServerPK = IntegerProperty(
                                        verbose_name = 'MinecraftServer\'s PK',
                                        required = True,
                                        )


    # When
    created = DateTimeProperty(
                               verbose_name = "Date Created",
                               required = True,
                               auto_now_add = True,
                               )
    modified = DateTimeProperty(
                               verbose_name = "Date Modified",
                               required = False,
                               default = None,
                               auto_now = True,
                               )


