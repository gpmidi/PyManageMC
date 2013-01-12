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
from django.contrib.auth.models import User
from extern.validators import validateHostIP
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    

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
                            help_text = "A short, computer friendly name for the access info. My only included letters, numbers, underscores, and hyphens. ",
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
    
class ServerInstance(models.Model):
    name = models.SlugField(
                            primary_key = True,
                            null = False,
                            blank = False,
                            max_length = 255,
                            db_index = True,
                            verbose_name = "Instance Name",
                            help_text = "A short, computer friendly name for the server instance. My only included letters, numbers, underscores, and hyphens. ",
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
                              help_text = "The user that is ultermatly responsable for this server instance",
                              )
    
    SERVER_STATUS = (
                       ('Active', (# 100-199
                            (100, "Active"),
                            (101, "On-Demand"),
                            )
                        ),
                     ('Inactive', (# 0-99
                            (0, "Created"),
                            (1, "Archived"),
                            (2, "Unknown"),
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
    
    
