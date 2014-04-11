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
import os, os.path, sys  # @UnusedImport
import re  # @UnusedImport

# Django
from django.db import models  # @UnusedImport
from django.conf import settings
from django.core.validators import *  # @UnusedWildImport
from django.core.exceptions import ValidationError  # @Reimport

# CouchDB
from couchdbkit.ext.django.schema import *  # @UnusedWildImport


def _getAdmin():
    if len(settings.ADMINS) <= 0:
        return (None, None, None)
    else:
        name, email = settings.ADMINS[0]
    sName = name.split(' ')
    if len(sName) == 1:
        return (name, '', email)
    elif len(sName) == 2:
        return (sName[0], sName[1], email)
    else:
        return (sName[0], ' '.join(sName[1:]), email)

_validatePackageListRE = re.compile(r'^[a-zA-Z\-_.]+$')
def _validatePackageList(value):
    try:
        values = list(value)  # @UnusedVariable
    except:
        raise ValidationError(u'%s is not itterable' % value)
    for value in values:
        if not _validatePackageListRE.match(value):
            raise ValidationError(u'%s is not a valid package name' % value)

_validateSSHKeyListRE = re.compile(r'^ssh-(rsa|dsa)\s+[a-zA-Z0-9+/]+([=]*)( [ a-zA-Z0-9+@./]+)?$')
def _validateSSHKeyList(value):
    try:
        values = list(value)  # @UnusedVariable
    except:
        raise ValidationError(u'%s is not itterable' % value)
    for value in values:
        if not _validatePackageListRE.match(value):
            raise ValidationError(u'%s is not a valid SSH public key' % value)

class DockerImage(Document):
    """ """
    humanName = StringProperty(
                          validators=[validate_slug, ],
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
        return map(lambda x: x.rstrip(), self.description)

    IMAGE_TYPES = (
                   # Not directly used; used as a platform for building other
                   # user images.
                   ('BaseImage', 'Base Image'),
                   # Visible to users and usable for running Minecraft
                   ('UserImage', 'UserImage'),
                   # ('',''),
                   )
    imageType = StringProperty(
                          validators=[validate_slug, ],
                          name="imageType",
                          required=True,
                          choices=IMAGE_TYPES,
                          default='BaseImage',
                          verbose_name="Image Type",
                          )
    imageID = StringProperty(
                          validators=[RegexValidator(r'^[a-f0-9]+$'), ],
                          name="dockerImageID",
                          required=True,
                          default=None,
                          verbose_name="Docker Image ID",
                          )

    parent = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9.\-]+(:?\:[0-9]+)?(?:\/[a-zA-Z0-9.\-]+)+(?:\:[a-zA-Z0-9.\-]+)?$'), ],
                          name="dockerParent",
                          required=True,
                          default="Ubuntu:13.10",
                          verbose_name="Docker Image Parent Image",
                          )

    def getFullDockerName(self):
        ret = ''
        if self.dockerIndexer:
            ret += self.dockerIndexer + "/"
        if self.repo:
            ret += str(self.repo) + '/'
        ret += self.dockerName
        if self.tag:
            ret += ":" + self.tag
        return ret

    dockerName = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9.\-]+$'), ],
                          name="dockerName",
                          required=True,
                          default=None,
                          verbose_name="Docker Image Name",
                          )
    dockerIndexer = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9.\-]+(:?\:[0-9]+)?$'), ],
                          name="dockerIndexer",
                          required=False,
                          default=None,
                          verbose_name="Docker Image Indexer",
                          )
    repo = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9.\-]+$'), ],
                          name="dockerRepo",
                          required=False,
                          default=None,
                          verbose_name="Docker Image Repo",
                          )
    tag = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9.\-]+$'), ],
                          name="dockerTag",
                          required=True,
                          default='latest',
                          verbose_name="Docker Image Tag",
                          )
    # The user that Minecraft runs as
    user = StringProperty(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9]+$'),
                                      MaxLengthValidator(14),
                                      MinLengthValidator(3),
                                      ],
                          name="minecraftUser",
                          required=True,
                          default='minecraft',
                          verbose_name="Minecraft Shell User & Group Name",
                          )
    uid = IntegerProperty(
                          validators=[
                                      MinValueValidator(1000),
                                      MaxValueValidator(5000),
                                      ],
                          name="minecraftUID",
                          required=True,
                          default=1000,
                          verbose_name="Minecraft Shell UID",
                          )
    gid = IntegerProperty(
                          validators=[
                                      MinValueValidator(1000),
                                      MaxValueValidator(5000),
                                      ],
                          name="minecraftGID",
                          required=True,
                          default=1000,
                          verbose_name="Minecraft Shell GID",
                          )
    minecraftUserPasswd = StringProperty(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'),
                                      MaxLengthValidator(128),
                                      MinLengthValidator(8),
                                      ],
                          name="minecraftUserPasswd",
                          required=False,
                          default=None,
                          verbose_name="Minecraft Shell User's Password",
                          )
    rootUserPasswd = StringProperty(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'),
                                      MaxLengthValidator(128),
                                      MinLengthValidator(8),
                                      ],
                          name="rootUserPasswd",
                          required=False,
                          default=None,
                          verbose_name="Root Shell User's Password",
                          )
    supervisordUser = StringProperty(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9]+$'),
                                      MaxLengthValidator(32),
                                      MinLengthValidator(4),
                                      ],
                          name="supervisordUser",
                          required=True,
                          default='admin',
                          verbose_name="Supervisord's Management Username",
                          )
    supervisordPasswd = StringProperty(
                          validators=[
                                      RegexValidator(r'^(\{[a-zA-Z0-9]+\})?[a-zA-Z0-9]+$'),
                                      MaxLengthValidator(512),
                                      MinLengthValidator(8),
                                      ],
                          name="minecraftUser",
                          required=True,
                          default=None,
                          verbose_name="Supervisord's Management Password Or Hash",
                          )
    supervisordAutoRestart = BooleanProperty(
                                     name="supervisordAutoRestart",
                                     required=True,
                                     default=True,
                                     verbose_name="Auto Restart Minecraft",
                                     )
    supervisordAutoStart = BooleanProperty(
                                     name="supervisordAutoStart",
                                     required=True,
                                     default=True,
                                     verbose_name="Auto Start Minecraft",
                                     )
    supervisordStartTimeSeconds = IntegerProperty(
                          validators=[
                                      MinValueValidator(1),
                                      MaxValueValidator(60 * 60),
                                      ],
                          name="supervisordStartTimeSeconds",
                          required=True,
                          default=16,
                          verbose_name="Time To Wait For Minecraft To Start (Seconds)",
                          )
    # An optional HTTP proxy for package download caching
    proxy = StringProperty(
                          validators=[URLValidator(), ],
                          name="httpProxy",
                          required=False,
                          default=None,
                          verbose_name="HTTP Proxy",
                          )
    # TODO: Improve package name validation
    extraPackages = StringListProperty(
                          validators=[_validatePackageList, ],
                          name="extraPackages",
                          required=True,
                          default=[],
                          verbose_name="Extra Packages",
                          )
    sshKeysRoot = StringListProperty(
                          validators=[_validateSSHKeyList, ],
                          name="sshKeysRoot",
                          required=True,
                          default=[],
                          verbose_name="Root's Authorized Keys",
                          )
    sshKeysMinecraft = StringListProperty(
                          validators=[_validateSSHKeyList, ],
                          name="sshKeysMinecraft",
                          required=True,
                          default=[],
                          verbose_name="Minecraft User's Authorized Keys",
                          )
    # Image Maintainer Info
    firstName = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'), ],
                          name="firstName",
                          required=True,
                          default=_getAdmin()[0],
                          verbose_name="Docker Maintainer's First Name",
                          )
    lastName = StringProperty(
                          validators=[RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'), ],
                          name="lastName",
                          required=True,
                          default=_getAdmin()[1],
                          verbose_name="Docker Maintainer's Last Name",
                          )
    email = StringProperty(
                          validators=[EmailValidator, ],
                          name="email",
                          required=True,
                          default=_getAdmin()[2],
                          verbose_name="Docker Maintainer's Email Address",
                          )
    # Minecraft server's java info
    javaArgs = StringListProperty(
                          validators=[ ],
                          name="javaArgs",
                          required=True,
                          default=[
                                   '-XX:+UseConcMarkSweepGC',
                                   '-XX:+CMSIncrementalPacing',
                                   '-XX:+AggressiveOpts',
                                   ],
                          verbose_name="Minecraft Server Args",
                          )
    javaBin = StringProperty(
                          validators=[ ],
                          name="javaBin",
                          required=True,
                          default='/usr/bin/java',
                          verbose_name="Java Binary",
                          )
    javaMaxMemMB = IntegerProperty(
                          validators=[
                                      MinValueValidator(128),
                                      MaxValueValidator(32 * 1024),
                                      ],
                          name="javaMaxMemMB",
                          required=True,
                          default=512,
                          verbose_name="Java Max Heap (MB) For Minecraft",
                          )
    javaInitMemMB = IntegerProperty(
                          validators=[
                                      MinValueValidator(128),
                                      MaxValueValidator(32 * 1024),
                                      ],
                          name="javaInitMemMB",
                          required=True,
                          default=64,
                          verbose_name="Java Initial Heap (MB) For Minecraft",
                          )
    javaGCThreads = IntegerProperty(
                          validators=[
                                      MinValueValidator(1),
                                      MaxValueValidator(128),
                                      ],
                          name="javaGCThreads",
                          required=True,
                          default=2,
                          verbose_name="Java GC Thread Count For Minecraft",
                          )

    def buildMCStartCmd(self):
        return "'%s' -Xmx%dM -Xms%dM -XX:ParallelGCThreads=%d %s -jar %s %s" % (
                self.javaBin,
                self.javaMaxMemMB,
                self.javaInitMemMB,
                self.javaGCThreads,
                ' '.join(self.javaArgs),
                '/var/lib/minecraft/minecraft_server.jar',
                'nogui',
                )













