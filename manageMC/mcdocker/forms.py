#!/usr/bin/python
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
'''
Created on May 3, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger('mcdocker.forms')

# Built-in
import os, os.path, sys  # @UnusedImport

# External
from django import forms
from django.core.validators import *

# Ours
from minecraft.models import *  # @UnusedWildImport
from mcdocker.models import *  # @UnusedWildImport
from mcdocker.tasks import *  # @UnusedWildImport
from mcdocker.models import _getAdmin


class BaseDockerInstanceForm(forms.Form):
    """
    """
    slug = forms.SlugField(
                            required=True,
                            label='FE Image Name',
                            validators=[
                                         validate_slug,
                                         MaxLengthValidator(64),
                                         MinLengthValidator(8),
                                         ],
                            help_text='Computer friendly name for this image',
                            )
    humanName = forms.CharField(
                                required=True,
                                label='Human Name',
                                help_text='Human friendly name for this image',
                                min_length=8,
                                max_length=128,
                                )
    description = forms.CharField(
                                required=True,
                                label='Human Name',
                                help_text='Human friendly name for this image',
                                default='',
                                min_length=0,
                                max_length=8192,
                                widget=forms.Textarea,
                                )
    dockerMemoryLimitMB = forms.IntegerField(
                           required=True,
                           default=512,
                           label='Docker Memory Limit (MiB)',
                           help_text='Max memory the Docker instance can use in MiB',
                           )
    dockerCPUShare = forms.IntegerField(
                           required=True,
                           default=64,
                           label='Docker CPU Share',
                           help_text='Relative CPU share',
                           )
    dockerName = forms.SlugField(
                            required=True,
                            label='Docker Image Name',
                            validators=[
                                         validate_slug,
                                         MaxLengthValidator(64),
                                         MinLengthValidator(4),
                                         RegexValidator(r'^[a-zA-Z0-9.\-]+$'),
                                         ],
                            help_text='Computer friendly name for this docker image',
                            )
    dockerIndexer = forms.CharField(
                            required=False,
                            label='Docker Indexer',
                            help_text='The hostname and port of the Docker Indexer, if any',
                            min_length=2,
                            max_length=128,
                            validators=[
                                        RegexValidator(r'^[a-zA-Z0-9.\-]+(:?\:[0-9]+)?$'),
                                        ],
                            )
    repo = forms.SlugField(
                            required=False,
                            label='Docker Repo Name',
                            default=None,
                            validators=[
                                         validate_slug,
                                         MaxLengthValidator(64),
                                         RegexValidator(r'^[a-zA-Z0-9.\-]+$'),
                                         ],
                            help_text='Docker repo image name',
                            )

    tag = forms.SlugField(
                            required=True,
                            label='Docker Image Tag',
                            default=None,
                            validators=[
                                         validate_slug,
                                         MaxLengthValidator(64),
                                         RegexValidator(r'^[a-zA-Z0-9.\-]+$'),
                                         ],
                            help_text='Tag the Docker image with this version ID',
                            )
    # The user that Minecraft runs as
    user = forms.CharField(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9]+$'),
                                      MaxLengthValidator(14),
                                      MinLengthValidator(3),
                                      ],
                          min_length=3,
                          max_length=14,
                          label="Minecraft Shell User/Group",
                          required=True,
                          default='minecraft',
                          help_text="The user and primary group name that Minecraft will run as",
                          )
    uid = forms.IntegerField(
                           required=True,
                           default=1000,
                           label='Minecraft Shell UID',
                           help_text="The UID to use for the Minecraft user's user",
                           validators=[
                                      MinValueValidator(1000),
                                      MaxValueValidator(5000),
                                      ],
                           )
    gid = forms.IntegerField(
                           required=True,
                           default=1000,
                           label='Minecraft Shell GID',
                           help_text="The GID to use for the Minecraft user's primary group",
                           validators=[
                                      MinValueValidator(1000),
                                      MaxValueValidator(5000),
                                      ],
                          )
    minecraftUserPasswd = forms.CharField(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'),
                                      MaxLengthValidator(128),
                                      MinLengthValidator(8),
                                      ],
                          min_length=8,
                          max_length=128,
                          label="Minecraft Shell User's Password",
                          required=False,
                          default=None,
                          help_text="The Minecraft shell user's password",
                          )
    rootUserPasswd = forms.CharField(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'),
                                      MaxLengthValidator(128),
                                      MinLengthValidator(8),
                                      ],
                          min_length=8,
                          max_length=128,
                          label="Root Shell User's Password",
                          required=False,
                          default=None,
                          help_text="The Root shell user's password",
                          )
    supervisordUser = forms.CharField(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9]+$'),
                                      MaxLengthValidator(32),
                                      MinLengthValidator(4),
                                      ],
                          min_length=4,
                          max_length=32,
                          label="Supervisord's Management Username",
                          required=True,
                          default='admin',
                          help_text="The Root shell user's password",
                          )
    supervisordPasswd = forms.CharField(
                          validators=[
                                      RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'),
                                      MaxLengthValidator(512),
                                      MinLengthValidator(8),
                                      ],
                          min_length=8,
                          max_length=128,
                          label="Supervisord's Management Password",
                          required=True,
                          default=None,
                          help_text="Supervisord's Management Password Or Hash For Config. Warning: This password is stored as-is in a file readable by all users in the Docker instance. ",
                          )
    # TODO: Need a better password storage system than a raw DB
    realSupervisordPasswd = forms.CharField(
                          validators=[
                                      RegexValidator(r'^(\{[a-zA-Z0-9]+\})?[a-zA-Z0-9]+$'),
                                      MaxLengthValidator(512),
                                      MinLengthValidator(8),
                                      ],
                          min_length=8,
                          max_length=512,
                          label="Supervisord's Management Password",
                          required=False,
                          default=None,
                          help_text="Supervisord's actual management password",
                          )
    supervisordAutoRestart = forms.BooleanField(
                                                required=True,
                                                default=True,
                                                label='Auto Restart Minecraft',
                                                )
    supervisordAutoStart = forms.BooleanField(
                                                required=True,
                                                default=True,
                                                label='Auto Start Minecraft',
                                                )
    supervisordStartTimeSeconds = forms.IntegerField(
                           required=True,
                           default=1000,
                           label='Minecraft Shell UID',
                           help_text="Time to wait for Minecraft to start in seconds",
                           validators=[
                                      MinValueValidator(1),
                                      MaxValueValidator(60 * 60),
                                      ],
                           )
    # An optional HTTP proxy for package download caching
    proxy = forms.URLField(
                           required=False,
                           default=None,
                           label="HTTP Proxy",
                           help_text="HTTP proxy that docker instances should use",
                           validators=[URLValidator(), ],
                           )

    # TODO: Improve package name validation
    extraPackages = forms.CharField(
                                    required=False,
                                    default='',
                                    label="Extra Packages",
                                    help_text="A list of extra packages to install in the Minecraft Docker instances",
                                    widget=forms.Textarea(),
                                    )
    # FIXME: Add validators
    sshKeysRoot = forms.CharField(
                                required=False,
                                default='',
                                label="Root's Authorized Keys",
                                help_text="A list of SSH keys to include for the root user",
                                widget=forms.Textarea(),
                                )
    # FIXME: Add validators
    sshKeysMinecraft = forms.CharField(
                                required=False,
                                default='',
                                label="Minecraft's Authorized Keys",
                                help_text="A list of SSH keys to include for the Minecraft user",
                                widget=forms.Textarea(),
                                )
    # Image Maintainer Info
    firstName = forms.CharField(
                                required=True,
                                default=_getAdmin()[0],
                                label="Docker Maintainer's First Name",
                                help_text="The first name of the person who maintains this Docker container",
                                validators=[RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'), ],
                                )
    lastName = forms.CharField(
                                required=True,
                                default=_getAdmin()[0],
                                label="Docker Maintainer's Last Name",
                                help_text="The last name of the person who maintains this Docker container",
                                validators=[RegexValidator(r'^[a-zA-Z0-9 \-_.]+$'), ],
                                )
    email = forms.EmailField(
                          validators=[EmailValidator, ],
                          required=True,
                          default=_getAdmin()[2],
                          verbose_name="Docker Maintainer's Email Address",
                          help_text="The email address of the person who maintains this Docker container",
                          )
    volumes = DictProperty(
                           validators=[],
                           name='volumes',
                           required=True,
                           default=settings.MINECRAFT_BASE_VOLUME_TYPES,
                           verbose_name="Volumes To Export",
                           )
    # Fixed port mappings to export
    # None==automatic random port
    ports = DictProperty(
           validators=[],
           name='ports',
           required=True,
           default={
            str(settings.MINECRAFT_DEFAULT_PORT_SSH):('0.0.0.0', None),
            str(settings.MINECRAFT_DEFAULT_PORT_SUPVD):('127.0.0.1', None),
            str(settings.MINECRAFT_DEFAULT_PORT_CONTAINER):('0.0.0.0', None),
            str(settings.MINECRAFT_DEFAULT_PORT_RCON):('127.0.0.1', None),
            '25580':('127.0.0.1', None),
            '25581':('127.0.0.1', None),
            '25582':('127.0.0.1', None),
            '25583':('127.0.0.1', None),
            '25584':('127.0.0.1', None),
            '25585':('127.0.0.1', None),
            '25586':('127.0.0.1', None),
            '25587':('127.0.0.1', None),
            '25588':('127.0.0.1', None),
            '25589':('127.0.0.1', None),
            },
           verbose_name="Ports To Export",
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





