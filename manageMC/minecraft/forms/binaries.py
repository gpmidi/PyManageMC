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
Created on Apr 6, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger('minecraft.forms.binaries')

# Built-in
import os, os.path, sys

# External
from django.forms import ModelForm, Form
from django import forms
from django.core import validators
from django.contrib.auth.models import User
from django.forms.fields import *
from django.forms.widgets import *

# Ours
from minecraft.models import *


class UploadBinaryForm(forms.Form):
    typeName = ChoiceField(
                           required=True,
                           choices=MinecraftServerBinary.TYPE_NAME_CHOICES,
                           initial='Stock',
                           label='Type Of Binary',
                           )
    releaseStatus = ChoiceField(
                           required=True,
                           choices=MinecraftServerBinary.RELEASE_STATUS_CHOICES,
                           initial='Production Release',
                           label='Type Of Release',
                           )
    version = CharField(
                        required=True,
                        initial=None,
                        label="Version",
                        )
    binary = FileField(
                       required=True,
                       label="Minecraft JAR",
                       )
    helperFiles = FileField(
                           required=False,
                           label="Helper Files (Overwrite)",
                           )
    helperFilesConfig = FileField(
                               required=False,
                               label="Helper Files (Configs)",
                               )
    
    
