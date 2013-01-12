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
from extern.validators import validateHostIP
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.contrib import admin


class News(models.Model):
    title = models.CharField(
                            null = False,
                            max_length = 1024,
                            verbose_name = "Title",
                            help_text = "Title of the post",
                            )
    body = models.TextField(
                            null = False,
                            blank = True,
                            verbose_name = "Body",
                            help_text = "",
                            )
    published = models.BooleanField(
                                    null = False,
                                    default = True,
                                    verbose_name = "Published",
                                    help_text = "Visible to external users",
                                    )
    frontpage = models.BooleanField(
                                    null = False,
                                    default = True,
                                    verbose_name = "Front Page?",
                                    help_text = "Visible on the front page",
                                    )
    created = models.DateTimeField(
                                   auto_now_add = True,
                                   null = False,
                                   verbose_name = "Created",
                                   help_text = "",
                                   )
    modified = models.DateTimeField(
                                   auto_now = True,
                                   null = False,
                                   verbose_name = "Last Modified",
                                   help_text = "",
                                   )

class NewsAdmin(admin.ModelAdmin):
    list_filter = (
                   'published',
                   'frontpage',
                   )
    list_display = (
                  'title',
                  'published',
                  'frontpage',
                  'created',
                  'modified',
                  )
    ordering = (
                '-created',
                ) 

admin.site.register(News, NewsAdmin)

class ExtraUserEmail(models.Model):
    profile = models.ForeignKey(
                                'UserProfile',
                                null = False,
                                )
    EMAIL_TYPES = (
                   (0, "Other"),
                   (1, "Personal"),
                   (2, "Work"),
                   (3, "ER Only"),
                   (4, "Automated Notifications"),
                   )
    emailType = models.SmallIntegerField(
                                         null = False,
                                         default = "Other",
                                         choices = EMAIL_TYPES,
                                         verbose_name = "Email Use",
                                         )
    email = models.EmailField(
                              null = False,
                              verbose_name = "Email Address",
                              )
    private = models.BooleanField(
                                null = False,
                                default = True,
                                verbose_name = "Private",
                                help_text = "Do not allow non-superusers to see this address. ",
                                )

admin.site.register(ExtraUserEmail)


class MinecraftUsername(models.Model):
    """ One of a minecraft user's in-game usernames """
    profile = models.ForeignKey(
                                'UserProfile',
                                null = False,
                                )
    username = models.EmailField(
                                 null = False,
                                 verbose_name = "Minecraft Username",
                                 max_length = 255,
                                 )
    private = models.BooleanField(
                                null = False,
                                default = True,
                                verbose_name = "Private",
                                help_text = "Do not allow non-superusers to see this username",
                                )
    verified = models.BooleanField(
                                   null = False,
                                   default = False,
                                   verbose_name = "Verified",
                                   help_text = "Has this address been verified",
                                   )
admin.site.register(MinecraftUsername)


class UserPhoneNumber(models.Model):
    profile = models.ForeignKey(
                                'UserProfile',
                                null = False,
                                )
    PHONE_TYPES = (
                   (0, "Personal Cell"),
                   (1, "Home Land Line"),
                   (2, "Work Cell"),
                   (3, "ER Only"),
                   (4, "Work Land Line"),
                   )
    phoneType = models.SmallIntegerField(
                                         null = False,
                                         default = "Personal Cell",
                                         choices = PHONE_TYPES,
                                         verbose_name = "Phone number Type",
                                         )
    phoneNumber = models.CharField(
                                   null = False,
                                   blank = False,
                                   verbose_name = "Phone Number",
                                   help_text = "The phone number, including area code and country code",
                                   )
    private = models.BooleanField(
                                null = False,
                                default = True,
                                verbose_name = "Private",
                                help_text = "Do not allow non-superusers to see this phone number",
                                )
admin.site.register(UserPhoneNumber)


class UserProfile(models.Model):
    user = models.OneToOneField(
                                User,
                                null = False,
                                verbose_name = "User",
                                )
    
    screenname = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Screen Name",
                            help_text = "The user's screenname. May only included letters, numbers, underscores, and hyphens. ",
                            )
    publicName = models.CharField(
                                  null = True,
                                  blank = True,
                                  max_length = 255,
                                  verbose_name = "The user's publicly visible name. Optional. ",
                                  )
    miscContactInfo = models.TextField(
                                       null = True,
                                       blank = True,
                                       max_length = 65536,
                                       verbose_name = "Miscellaneous Contact Info",
                                       )
admin.site.register(UserProfile)


class ServerInstanceExternalInfo(models.Model):
    """ Information to access a server - ie hostname/IP and port
    """
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Access Name",
                            help_text = "A short, computer friendly name for the access info. May only included letters, numbers, underscores, and hyphens. ",
                            )
    host = models.CharField(
                            null = False,
                            blank = False,
                            max_length = 8192,
                            verbose_name = "Host/IP",
                            help_text = "The hostname or IP address used by remote users",
                            validators = [
                                          validateHostIP,
                                          MinLengthValidator(min_length = 2),
                                          ],
                            )
    port = models.IntegerField(
                               null = False,
                               default = 25565,
                               verbose_name = "Port",
                               help_text = "The TCP port that users connect to",
                               validators = [
                                             MinValueValidator(1),
                                             MaxValueValidator(65535),
                                             ],
                               )
    instance = models.ForeignKey(
                                 'ServerInstanceExternalInfo',
                                 null = False,
                                 verbose_name = "Server Instance",
                                 help_text = "The server instance that this access is for",
                                 )
admin.site.register(ServerInstanceExternalInfo)


class ServerSystem(models.Model):
    """ A physical or virtual system that one or more Minecraft servers run on """
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "System Name",
                            help_text = "A short, computer friendly name for this system/server/box. May only included letters, numbers, underscores, and hyphens. ",
                            )
    admins = models.ManyToManyField(
                                    User,
                                    null = False,
                                    verbose_name = "Admins",
                                    help_text = "Users who have administrative access to this server",
                                    )
    owner = models.ForeignKey(
                              User,
                              null = False,
                              blank = False,
                              verbose_name = "Owner",
                              help_text = "The user that is ultimately responsible for this server",
                              )
admin.site.register(ServerSystem)
   

class ServerSystemIPs(models.Model):
    """ An internal IP address of a physical or virtual system that one or more Minecraft servers run on """
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "System IP Name",
                            help_text = "A short, computer friendly name for this IP. May only included letters, numbers, underscores, and hyphens. ",
                            )
    ip = models.IPAddressField(
                               null = False,
                               verbose_name = "IP",
                               )
    system = models.ForeignKey(
                               ServerSystem,
                               verbose_name = "System",
                               )
admin.site.register(ServerSystemIPs)


class ServerInstance(models.Model):
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Instance Name",
                            help_text = "A short, computer friendly name for the server instance. May only included letters, numbers, underscores, and hyphens. ",
                            )
    admins = models.ManyToManyField(
                                    User,
                                    null = False,
                                    verbose_name = "Admins",
                                    help_text = "Users who have administrative access to this server instance",
                                    )
    owner = models.ForeignKey(
                              User,
                              null = False,
                              blank = False,
                              verbose_name = "Owner",
                              help_text = "The user that is ultimately responsible for this server instance",
                              )
    
    SERVER_STATUS = (
                       ('Active', (# 100-199
                            (100, "Active"),
                            (101, "On-Demand"),
                            (102, "On-Hold"),
                            )
                        ),
                     ('Inactive', (# 0-99
                            (0, "Created"),
                            (1, "Archived"),
                            (2, "Unknown"),
                            (3, "Deleted"),
                            )
                        ),
                   )
    status = models.SmallIntegerField(
                                      null = False,
                                      default = "Created",
                                      choices = SERVER_STATUS,
                                      verbose_name = "Status",
                                      )
    humanName = models.SlugField(
                            null = False,
                            blank = False,
                            max_length = 255,
                            verbose_name = "Human Name",
                            help_text = "A short, human friendly name for this server",
                            )
    description = models.TextField(
                                   null = False,
                                   blank = True,
                                   default = '',
                                   max_length = 8192,
                                   verbose_name = "Description",
                                   help_text = "A description and other useful info",
                                   )
    system = models.ForeignKey(
                               ServerSystem,
                               null = False,
                               verbose_name = "System",
                               help_text = "The server/system/box/etc that this Minecraft server instance runs on",
                               )
    internalIP = models.IPAddressField(
                               null = False,
                               verbose_name = "Internal IP",
                               help_text = "The internal IP address of the server",
                               )
    port = models.IntegerField(
                               null = False,
                               default = 25565,
                               verbose_name = "Port",
                               help_text = "The TCP port that the server listens on",
                               validators = [
                                             MinValueValidator(1),
                                             MaxValueValidator(65535),
                                             ],
                               )
admin.site.register(ServerInstance)
