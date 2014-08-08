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
Created on Apr 11, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger('mcdocker.views')

# Built-in
import os, os.path, sys  # @UnusedImport
import urllib

# External
from django.core.exceptions import ObjectDoesNotExist  # @UnusedImport
from django.shortcuts import render_to_response, get_object_or_404, render, redirect  # @UnusedImport
from django.db.models import Q  # @UnusedImport
from django.template import RequestContext  # @UnusedImport
from django.contrib.auth.models import AnonymousUser  # @UnusedImport
from django.views.decorators.cache import cache_page  # @UnusedImport
from django.core.paginator import Paginator, EmptyPage, InvalidPage  # @UnusedImport
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from couchdbkit.exceptions import ResourceNotFound  # @UnusedImport

# Ours
from minecraft.models import *  # @UnusedWildImport
from mcdocker.models import *  # @UnusedWildImport
from mcdocker.tasks import *  # @UnusedWildImport
from mcdocker.forms import *  # @UnusedWildImport


@login_required
@permission_required('mcdocker.view_dockerimage')
def dockerImageIndex(req):
    """ Docker Image index """
    return render_to_response(
                              'mcdocker/dockerMgmt/index.djhtml',
                              dict(
                                   allImages=DockerImage.view('mcdocker/allOSImages'),
                                   baseImages=DockerImage.view('mcdocker/baseOSImages'),
                                   userImages=DockerImage.view('mcdocker/userOSImages'),
                                   ),
                              context_instance=RequestContext(req),
                              )


@login_required
@permission_required('mcdocker.view_dockerimage')
@permission_required('mcdocker.change_dockerimage')
def dockerImageEdit(req, dockerImageName):
    """ Docker Image Change """
    try:
        return render_to_response(
                                  'mcdocker/dockerMgmt/edit.djhtml',
                                  dict(
                                       image=DockerImage.get(dockerImageName),
                                       ),
                                  context_instance=RequestContext(req),
                                  )
    except ResourceNotFound:
        raise Http404("Couldn't find an image named %r" % dockerImageName)


@login_required
@permission_required('mcdocker.view_dockerimage')
@permission_required('mcdocker.add_dockerimage')
def dockerImageCreate(req):
    """ Docker Image Add """
    if req.method == 'POST':
        form = BaseDockerInstanceForm(req.POST)
        if form.is_valid():
            di = DockerImage(
                             _id=form.slug,
                             humanName=form.humanName,

                             )
            # model = form.save()
            return redirect('dockerImageEdit', di._id)
    else:
        form = BaseDockerInstanceForm()

    return render_to_response(
                              'mcdocker/dockerMgmt/add.djhtml',
                              dict(
                                   form=form,
                                   ),
                              context_instance=RequestContext(req),
                              )


@login_required
@permission_required('mcdocker.view_dockerimage')
@permission_required('mcdocker.add_dockerimage')
@permission_required('mcdocker.add_basedockerimage')
def dockerBaseImageCreate(req):
    """ Docker Image Add """
    if req.method == 'POST':
        form = BaseDockerInstanceForm(req.POST)
        if form.is_valid():
            # TODO: Catch model validation errors and pass to user as something friendly
            di = DockerImage(
                             _id=form.slug,
                             humanName=form.humanName,
                             description=form.description,
                             imageType='BaseImage',
                             imageID=None,
                             # TODO: Stop hard coding this
                             parent='ubuntu:14.04',
                             dockerMemoryLimitMB=form.dockerMemoryLimitMB,
                             dockerCPUShare=form.dockerCPUShare,
                             dockerName=form.dockerName,
                             dockerIndexer=form.dockerIndexer,
                             repo=form.repo,
                             tag=form.tag,
                             user=form.user,
                             uid=form.uid,
                             gid=form.gid,
                             minecraftUserPasswd=None,
                             rootUserPasswd=None,
                             supervisordUser=form.supervisordUser,
                             supervisordPasswd=None,
                             supervisordAutoRestart=form.supervisordAutoRestart,
                             supervisordAutoStart=form.supervisordAutoStart,
                             supervisordStartTimeSeconds=form.supervisordStartTimeSeconds,
                             proxy=form.proxy,
                             extraPackages=map(lambda x: x.rstrip(), form.extraPackages.splitlines()),
                             sshKeysRoot=map(lambda x: x.rstrip(), form.sshKeysRoot.splitlines()),
                             sshKeysMinecraft=map(lambda x: x.rstrip(), form.sshKeysMinecraft.splitlines()),
                             firstName=form.firstName,
                             lastName=form.lastName,
                             email=form.email,
                             javaMaxMemMB=form.javaMaxMemMB,
                             javaInitMemMB=form.javaInitMemMB,
                             javaGCThreads=form.javaGCThreads,
                             )
            di.save()
            return redirect('dockerImageEdit', di._id)
    else:
        form = BaseDockerInstanceForm()

    return render_to_response(
                              'mcdocker/dockerMgmt/add.djhtml',
                              dict(
                                   form=form,
                                   ),
                              context_instance=RequestContext(req),
                              )



