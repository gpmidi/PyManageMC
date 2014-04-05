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
from django.core.validators import MinLengthValidator, MaxValueValidator
from django.core.validators import validate_slug, MinValueValidator

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
    def __str__(self):
        return "News %r...(%s)" % (self.title[:75], self.created)



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
    
    def __str__(self):
        return "Email %r" % self.email


class MinecraftUsername(models.Model):
    """ One of a minecraft user's in-game usernames """
    verbose_name = "minecraft username"
    verbose_name_plural = "minecraft usernames"
    profile = models.ForeignKey(
                                'UserProfile',
                                null = False,
                                )
    username = models.CharField(
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
    def __str__(self):
        return "MC %s" % self.username


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
    def __str__(self):
        return "Phone Number %s" % self.phoneNumber    


class UserProfile(models.Model):
    verbose_name = "user info"
    verbose_name_plural = "user info"

    user = models.OneToOneField(
                                User,
                                primary_key = True,
                                null = False,
                                verbose_name = "User",
                                editable = False,
                                )
    screenname = models.SlugField(
                            unique = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Screen Name",
                            help_text = "The user's screenname. May only included letters, numbers, underscores, and hyphens. ",
                            validators = [ validate_slug, ],
                            )
    publicName = models.CharField(
                                  null = True,
                                  blank = True,
                                  max_length = 255,
                                  verbose_name = "The user's publicly visible name. Should NOT be a screenname. Optional. ",
                                  )
    miscContactInfo = models.TextField(
                                       null = True,
                                       blank = True,
                                       max_length = 65536,
                                       verbose_name = "Miscellaneous Contact Info",
                                       )
    
    def __str__(self):
        return "%s's Profile" % self.user.username


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
                            validators = [ validate_slug, ],
                            )
    ip = models.IPAddressField(
                               null = False,
                               verbose_name = "IP",
                               )
    system = models.ForeignKey(
                               'ServerSystem',
                               verbose_name = "System",
                               )
    def __str__(self):
        return "System IP %s(%s)" % (self.name, self.ip)


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
                            validators = [ validate_slug, ],
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
        return "System %s" % self.name


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
                            validators = [ validate_slug, ],
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
    def __str__(self):
        return "ExternalInfo %s" % self.name
   

class ServerInstance(models.Model):
    class Meta:
        permissions = (
            ("view_serverinstance", "Can see all instances"),
            )
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Instance Name",
                            help_text = "A short, computer friendly name for the server instance. May only included letters, numbers, underscores, and hyphens. ",
                            validators = [ validate_slug, ],
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
    
    # @warning: Both the status name and the group name MUST be valid as-is in URLs
    SERVER_STATUS = (
                       ('Active', (
                            ('active', "Always Active"),
                            ('ondemand', "On-Demand"),
                            )
                        ),
                     ('Inactive', (
                            ('created', "Created"),
                            ('archived', "Archived"),
                            ('unknown', "Unknown"),
                            ('deleted', "Deleted"),
                            ('onhold', "On-Hold"),
                            )
                        ),
                   )
    status = models.CharField(
                              null = False,
                              default = "created",
                              max_length = 32,
                              choices = SERVER_STATUS,
                              verbose_name = "Status",
                              )
    humanName = models.CharField(
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
    
    
    @classmethod
    def listStatusGroups(cls, forceLowerCase = False):
        """ List out all status groups """
        groups = []
        for group, statuses in cls.SERVER_STATUS:
            if forceLowerCase:
                groups.append(group.lower())
            else:
                groups.append(group)
        return groups
    
    
    @classmethod
    def listStatuses(cls, forceLowerCase = False, retActualName = False):
        """ List out all statuses 
        @param forceLowerCase: All returned data should be in lowercase
        @param retActualName: Return the name stored in the DB, not the "Pretty" name  
        """
        ret = []
        for group, statuses in cls.SERVER_STATUS:
            for actualName, name in statuses:
                if retActualName:
                    value = actualName
                else:
                    value = name
                if forceLowerCase:
                    value = value.lower()
                ret.append(value)
        return ret
    
    
    @classmethod
    def listStatusFull(cls):
        """ Return a list of all statuses as (actualName,humanName)  
        """
        ret = []
        for group, statuses in cls.SERVER_STATUS:
            for stat in statuses:
                ret.append(stat)
        return ret
    
    
    @classmethod
    def statusGroup(cls, group, refrenceType = "Pretty", exactCase = False):
        groups = []
        for checkGroup, statuses in cls.SERVER_STATUS:
            groups.append(checkGroup)
            if (group == checkGroup and exactCase) or (group.lower() == checkGroup.lower() and not exactCase):
                if refrenceType == "Pretty":
                    # Element one (the "human name") for the status
                    return map(lambda x: x[1], statuses)
                elif refrenceType == "Actual":
                    # Element zero - The raw value stored in the DB
                    return map(lambda x: x[0], statuses)
                else:
                    raise ValueError("Reference type must be Pretty or Actual, not %r" % refrenceType)
        raise ValueError("Group %r is not a valid server status group. Valid choices: %r" % (group, groups))
    
    
    def checkUser(self,req,perms='admin'):
        if req.user in self.admins or req.user == self.owner:
            return True
        return False


    def getServer(self):
        """ Returns the minecraft server object for hosted instances
        or None if it is not hosted """
        from minecraft.models import MinecraftServer
        try:
            return MinecraftServer.objects.get(pk = self.name)
        except MinecraftServer.DoesNotExist as e:
            return None

    
    def __str__(self):
        return "Instance %s" % self.name
    
