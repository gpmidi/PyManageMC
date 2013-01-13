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
Created on Jan 12, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404

import datetime

from extern.models import *

def instance(req, instanceSlug):
    """ Display a server instance """
    inst = get_object_or_404(ServerInstance, name = instanceSlug)
    return render_to_response(
                              'instance.html',
                              dict(
                                   instance = inst,
                                   ),
                              context_instance = RequestContext(req),
                              )


def instances(req, statusIs = None, statusIsInGroup = None):
    """ Display all server instances """
    inst = ServerInstance.objects.all()
    if statusIs is not None:
        inst = inst.filter(status = statusIs)
    if statusIsInGroup is not None:
        try:
            inst = inst.filter(status__in = ServerInstance.statusGroup(statusIsInGroup, refrenceType = "Actual", exactCase = False))
        except ValueError, e:
            raise Http404("Invalid group %r" % statusIsInGroup)
    groups = ServerInstance.listStatusGroups(forceLowerCase = True)
    statuses = ServerInstance.listStatusFull()
    return render_to_response(
                              'instances.html',
                              dict(
                                   serverInstances = inst,
                                   serverStatusGroups = groups,
                                   serverStatuses = statuses,
                                   ),
                              context_instance = RequestContext(req),
                              )
