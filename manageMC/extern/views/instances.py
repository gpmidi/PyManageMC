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
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404

import datetime

from extern.models import *
from extern.forms import *


@login_required
@permission_required('extern.add_serverinstance')
def newInstanceNonAdmin(req):
    if req.method=='POST':
        form = ServerInstanceNonAdminForm(
                                          req.POST,
                                          )
        if form.is_valid():
            model = form.save(commit = False)
            model.owner = req.user
            model.save()
            return redirect('/e/instances/instance/%s/' % model.name)
    else:
        form = ServerInstanceNonAdminForm()
    return render_to_response(
                              'extern/newInstance.html',
                              dict(
                                   form = form,
                                   ),
                              context_instance = RequestContext(req),
                              )


def _isAdmin(user):
    return user.is_staff

@login_required
@permission_required('extern.add_serverinstance')
@user_passes_test(_isAdmin)
def newInstanceAdmin(req):
    if req.method == 'POST':
        form = ServerInstanceAdminForm(req.POST)
        if form.is_valid():
            model = form.save()
            return redirect('/e/instances/instance/%s/' % model.name)
    else:
        form = ServerInstanceAdminForm()
    return render_to_response(
                              'extern/newInstance.html',
                              dict(
                                   form=form,
                                   ),
                              context_instance = RequestContext(req),
                              )
    

@permission_required('extern.view_serverinstance')
def instance(req, instanceSlug):
    """ Display a server instance """
    inst = get_object_or_404(ServerInstance, name = instanceSlug)
    return render_to_response(
                              'extern/instance.html',
                              dict(
                                   instance = inst,
                                   ),
                              context_instance = RequestContext(req),
                              )


@permission_required('extern.delete_serverinstance')
def deleteInstance(req, instanceSlug):
    """ Display a server instance """
    inst = get_object_or_404(ServerInstance, name = instanceSlug)
    if req.method=='POST':
        if req.POST['confirmed']==inst.name:
            inst.delete()
            return redirect('/e/instances/')
    return render_to_response(
                              'extern/deleteInstance.html',
                              dict(
                                   instance = inst,
                                   ),
                              context_instance = RequestContext(req),
                              )


@permission_required('extern.view_serverinstance')
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
                              'extern/instances.html',
                              dict(
                                   serverInstances = inst,
                                   serverStatusGroups = groups,
                                   serverStatuses = statuses,
                                   ),
                              context_instance = RequestContext(req),
                              )
