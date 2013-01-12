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
    verbose_name = "news"
    verbose_name_plural = "news"
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
    verbose_name = "user email"
    verbose_name_plural = "user emails"
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
                                help_text = "Allow only superusers to see this",
                                )
    public = models.BooleanField(
                                null = False,
                                default = False,
                                verbose_name = "Public",
                                help_text = "Allow unauthenticated users to see this",
                                )

class ExtraUserEmailInline(admin.TabularInline):
    model = ExtraUserEmail


class MinecraftUsername(models.Model):
    """ One of a minecraft user's in-game usernames """
    verbose_name = "minecraft username"
    verbose_name_plural = "minecraft usernames"
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
                                help_text = "Allow only superusers to see this",
                                )
    public = models.BooleanField(
                                null = False,
                                default = False,
                                verbose_name = "Public",
                                help_text = "Allow unauthenticated users to see this",
                                )
    verified = models.BooleanField(
                                   null = False,
                                   default = False,
                                   verbose_name = "Verified",
                                   help_text = "Has this address been verified",
                                   )
class MinecraftUsernameInline(admin.TabularInline):
    model = MinecraftUsername


class UserPhoneNumber(models.Model):
    verbose_name = "phone number"
    verbose_name_plural = "phone numbers"
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
                                   max_length = 64,
                                   verbose_name = "Phone Number",
                                   help_text = "The phone number, including area code and country code",
                                   )
    private = models.BooleanField(
                                null = False,
                                default = True,
                                verbose_name = "Private",
                                help_text = "Allow only superusers to see this",
                                )
    public = models.BooleanField(
                                null = False,
                                default = False,
                                verbose_name = "Public",
                                help_text = "Allow unauthenticated users to see this",
                                )
            
class UserPhoneNumberInline(admin.TabularInline):
    model = UserPhoneNumber


class UserProfile(models.Model):
    verbose_name = "user info"
    verbose_name_plural = "user info"
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
    
    def __str__(self):
        return "%s's Profile" % self.user.username

class UserProfileAdmin(admin.ModelAdmin):
    inlines = [
        MinecraftUsernameInline,
        ExtraUserEmailInline,
        UserPhoneNumberInline,
    ]

admin.site.register(UserProfile, UserProfileAdmin)


class ServerSystemIPs(models.Model):
    """ An internal IP address of a physical or virtual system that one or more Minecraft servers run on """
    verbose_name = "system ip"
    verbose_name_plural = "system ip"
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "IP Name",
                            help_text = "A short, computer friendly name for this IP. May only included letters, numbers, underscores, and hyphens. ",
                            )
    ip = models.IPAddressField(
                               null = False,
                               verbose_name = "IP",
                               )
    system = models.ForeignKey(
                               'ServerSystem',
                               verbose_name = "System",
                               )
class ServerSystemIPsInline(admin.TabularInline):
    model = ServerSystemIPs


class ServerSystem(models.Model):
    """ A physical or virtual system that one or more Minecraft servers run on """
    verbose_name = "system"
    verbose_name_plural = "systems"
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
                                    related_name = "serveradmins",
                                    null = False,
                                    verbose_name = "Admins",
                                    help_text = "Users who have administrative access to this server",
                                    )
    owner = models.ForeignKey(
                              User,
                              related_name = "serverowners",
                              null = False,
                              blank = False,
                              verbose_name = "Owner",
                              help_text = "The user that is ultimately responsible for this server",
                              )
    
    def __str__(self):
        return "System %r" % self.name

class ServerSystemAdmin(admin.ModelAdmin):
    inlines = [
               ServerSystemIPsInline,
    ]

admin.site.register(ServerSystem, ServerSystemAdmin)


class ServerInstanceExternalInfo(models.Model):
    """ Information to access a server - ie hostname/IP and port
    """
    verbose_name = "external info"
    verbose_name_plural = "external info"
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Name/Description",
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
                                          MinLengthValidator(2),
                                          ],
                            )
    ip = models.IPAddressField(
                            null = False,
                            blank = False,
                            verbose_name = "IP",
                            help_text = 'The external IP address used to access the server. If an IP is given for "Host/IP", it should match this. ',
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
                                 'ServerInstance',
                                 null = False,
                                 verbose_name = "Server Instance",
                                 help_text = "The server instance that this access is for",
                                 )
    
class ServerInstanceExternalInfoInline(admin.TabularInline):
    model = ServerInstanceExternalInfo
   
   
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
                                    related_name = "instanceadmins",
                                    verbose_name = "Admins",
                                    help_text = "Users who have administrative access to this server instance",
                                    )
    owner = models.ForeignKey(
                              User,
                              null = False,
                              related_name = "instanceowners",
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
                               verbose_name = "Internal Port",
                               help_text = "The TCP port that the server listens on internally",
                               validators = [
                                             MinValueValidator(1),
                                             MaxValueValidator(65535),
                                             ],
                               )
    
    
class ServerInstanceAdmin(admin.ModelAdmin):
    inlines = [
        ServerInstanceExternalInfoInline,
    ]
    
admin.site.register(ServerInstance, ServerInstanceAdmin)
