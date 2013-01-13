'''
Created on May 4, 2012

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.forms import ModelForm, Form
from django import forms
from django.core import validators
from django.contrib.auth.models import User

from mcer.minecraft.models import *

class EditServerForm(ModelForm):
    class Meta:
        model = MinecraftServer
