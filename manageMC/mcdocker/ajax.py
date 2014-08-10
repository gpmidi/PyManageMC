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
Created on Aug 9, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger('mcdocker.ajax')

# Built-in

# External
from dajax.core import Dajax  # @UnresolvedImport
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from django.http import Http404
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from dajaxice.decorators import dajaxice_register
from django.contrib.auth.decorators import login_required

# Ours
from mcdocker.models import *
from mcdocker.tasks import *


# @dajaxice_register
# @login_required
# def buildDockerImage(req, imageId):
#     """ Build the given docker image """
#     try:
#         di = DockerImage.get(imageId)
#
#     except Exception, e:
#         log.exception("Failed to start docker build for %r", imageId)
#         dajax = Dajax()
#         dajax.assign('#dockerImageBuildButton', 'innerHTML', 'Failed')
#         return dajax.json()
#
#     res = stop.delay(server_pk)
#     res.wait()
#     dajax = Dajax()
#     # dajax.assign('#adminActionLog', 'innerHTML', 'Stopping server...\n')
#     dajax.prepend('#messageList', 'innerHTML', _makeMessage(server_pk, 'Stopping server...'))
#     return dajax.json()
