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
Created on Apr 29, 2012

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from dajax.core import Dajax  # @UnresolvedImport
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.http import Http404
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import os.path 
from mimetypes import guess_type
from django.contrib.auth import authenticate, login
from dajaxice.core import dajaxice_functions  # @UnresolvedImport

from minecraft.models import *
from minecraft.tasks import *

def login_a(req, username, password):
    user = authenticate(username = username, password = password)
    if user is not None:
        if user.is_active:
            login(req, user,)
            dajax = Dajax()
            dajax.assign('input#sidebarUsername', 'type', 'hidden')
            dajax.assign('input#sidebarPassword', 'type', 'hidden')
            dajax.assign('input#sidebarButton', 'type', 'hidden')
            dajax.assign('label#sidebarUsernameLabel', 'innerHTML', '')
            dajax.assign('label#sidebarPasswordLabel', 'innerHTML', '')
            dajax.assign('p#loginfieldhelp', 'innerHTML', '')
            dajax.assign('input#crtboxbutton', 'value', 'Save')
            dajax.assign('input#crtboxbutton', 'disabled', '')
            dajax.remove('#loginForm')
            dajax.redirect('/servers/')
            return dajax.json()
        else:
            dajax = Dajax()
            dajax.assign('p#loginfieldhelp', 'innerHTML', 'Account Disabled!')
            return dajax.json()
    else:
        dajax = Dajax()
        dajax.assign('p#loginfieldhelp', 'innerHTML', 'Invalid Login!')
        return dajax.json()

dajaxice_functions.register(login_a)

def server_stop(req, server_pk):
    """ Stop a server """
    res = stop.delay(server_pk)
    res.wait()
    dajax = Dajax()
    dajax.assign('div#serverstatus', 'innerHTML', 'Stopped')
    return dajax.json()

dajaxice_functions.register(server_stop)

def server_start(req, server_pk):
    """ Start a server """
    res = start.delay(server_pk)
    res.wait()
    dajax = Dajax()
    dajax.assign('div#serverstatus', 'innerHTML', 'Running')
    return dajax.json()

dajaxice_functions.register(server_start)

def server_say(req, server_pk, message):
    """ Say something in a server """
    res = say.delay(server_pk, message)
    dajax = Dajax()
    dajax.assign('input#servermessage', 'value', '')
    return dajax.json()

dajaxice_functions.register(server_say)
