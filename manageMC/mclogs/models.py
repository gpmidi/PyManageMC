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
from django.conf import settings
from django.core.validators import MinLengthValidator, MaxValueValidator
from django.core.validators import validate_slug, MinValueValidator

# CouchDB
from couchdbkit.ext.django.schema import *

# Load serverType objects
from mclogs.validators import *


class MinecraftServerLogFileArchive(Document):
    """ A Minecraft server's post-rotation log file
    """
    class Meta:
        app_label = 'manageMC.mclogs'

    serverId = StringProperty(
                             verbose_name = 'Server ID',
                             default = None,
                             required = True,
                             )
    FLOW_TYPES = (
                  ('STDIN', 'STDIN'),
                  ('STDOUT', 'STDOUT'),
                  ('STDERR', 'STDERR'),
                  ('FILE', 'File'),
                  ('UNK', 'Unknown'),
                  )
    flow = StringProperty(
                         verbose_name = 'Flow Type',
                         default = 'UNK',
                         required = True,
                         choices = FLOW_TYPES,
                         )
    LOG_TYPES = (
                 ('stdio','stdio'),
                 ('file','file'),
                 ('unknown','unknown'),
                 )
    logType = StringProperty(
                             verbose_name = 'Log File Type',
                             default = 'unknown',
                             required = True,
                             choices = LOG_TYPES,
                             )
    filename = StringProperty(
                             verbose_name = 'Log File Name',
                             default = None,
                             required = True,
                             )
    COMPRESSION_TYPES = (
                         ('None', 'None'),
                         ('GZIP', 'GZIP'),
                         ('LZO', 'LZO'),
                         ('BZIP2', 'BZIP2'),
                         ('ZIP', 'ZIP'),
                         )
    compression = StringProperty(
                             verbose_name = 'Log File Compression Type',
                             default = 'None',
                             required = True,
                             choices = COMPRESSION_TYPES,
                             )
    begining = DateTimeProperty(
                                verbose_name = 'Timestamp of first log',
                                required = False,
                                default = None,
                                )
    ending = DateTimeProperty(
                                verbose_name = 'Timestamp of last log',
                                required = False,
                                default = None,
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



# class MinecraftServerLogLines(Document):
#     """ A Minecraft server's log files
#     """
#     class Meta:
#         app_label = 'manageMC.mclogs'
#
#     # When
#     created = DateTimeProperty(
#                                verbose_name = "Date Created",
#                                required = True,
#                                auto_now_add = True,
#                                )
#     logLine = StringProperty(
#                              verbose_name = "Log Type",
#                              required = True,
#                              )
#
#
# class MinecraftServerLogFile(DocumentSchema):
#     """ One of a Minecraft server's log files
#     """
#     class Meta:
#         app_label = 'manageMC.mclogs'
#     # Standard In, Out, and Error
#     LOGTYPE_STDIO = "stdio"
#     # A on-disk log file
#     LOGTYPE_FILE = "file"
#     # Unknown
#     LOGTYPE_UNK = "unknown"
#
#     logType = StringProperty(
#                              verbose_name = "Log Type",
#                              default = LOGTYPE_UNK,
#                              required = True,
#                              choices = [
#                                         LOGTYPE_STDIO,
#                                         LOGTYPE_FILE,
#                                         LOGTYPE_UNK,
#                                         ],
#                              )
#     # A list of the keys of recent log lines
#     rawLogLines = SchemaListProperty(
#                                      MinecraftServerLogLine,
#                                      verbose_name = "Raw Log Lines",
#                                      required = True,
#                                      default = [],
#                                      )
#
#     # When
#     created = DateTimeProperty(
#                                verbose_name = "Date Created",
#                                required = True,
#                                auto_now_add = True,
#                                )
#     modified = DateTimeProperty(
#                                verbose_name = "Date Modified",
#                                required = False,
#                                default = None,
#                                auto_now = True,
#                                )
#
#     # File Properties
#     # None if not relevant for the given type of IO
#     atime = DateTimeProperty(
#                                verbose_name = "Date File Last Accessed",
#                                required = True,
#                                )
#     ctime = DateTimeProperty(
#                                verbose_name = "Date File Created",
#                                required = True,
#                                )
#     mtime = DateTimeProperty(
#                                verbose_name = "Date File Last Modified",
#                                required = True,
#                                )
#
#
# class MinecraftServerLogs(Document):
#     """ A Minecraft server's log files
#     """
#     class Meta:
#         app_label = 'manageMC.mclogs'
#
#     @classmethod
#     def makeServerID(cls, minecraftServerPK):
#         """ Create the _id used  """
#         # FIXME: Should 'cls' be 'ServerProperitiesConfigFileType'?
#         return "%s-%s" % (cls.__name__, minecraftServerPK)
#
#     # Standard Info
#     logs = SchemaDictProperty(
#                             MinecraftServerLogFile,
#                             verbose_name = 'Config File Type Name',
#                             default = 'ServerProperitiesConfigFileType',
#                             required = False,
#                             )
#
#     minecraftServerPK = IntegerProperty(
#                                         verbose_name = 'MinecraftServer\'s PK',
#                                         required = True,
#                                         )
#
#
#     # When
#     created = DateTimeProperty(
#                                verbose_name = "Date Created",
#                                required = True,
#                                auto_now_add = True,
#                                )
#     modified = DateTimeProperty(
#                                verbose_name = "Date Modified",
#                                required = False,
#                                default = None,
#                                auto_now = True,
#                                )

