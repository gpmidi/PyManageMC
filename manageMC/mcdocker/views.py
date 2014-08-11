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
@permission_required('mcdocker.change_dockerimage')
def dockerImageBuild(req, dockerImageId):
    """ Docker Image Change """
    try:
        di = DockerImage.get(dockerImageId)
        job = doBuildImage(di=di)
        return redirect('DockerImageEdit', di._id)
    except ResourceNotFound:
        raise Http404("Couldn't find an image with id %r" % dockerImageId)


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
        form = NewDockerInstanceForm(req.POST)
        if form.is_valid():
            di = DockerImage(
                             _id=form.cleaned_data['itag'],
                             humanName=form.cleaned_data['humanName'],
                             humanDescription=form.cleaned_data['description'],
                             imageType='UserImage',
                             imageID=None,
                             dockerParent=form.cleaned_data['baseImage'],
                             dockerMemoryLimitMB=form.cleaned_data['dockerMemoryLimitMB'],
                             dockerCPUShare=form.cleaned_data['dockerCPUShare'],
                             dockerName=form.cleaned_data['dockerName'],
                             dockerIndexer=form.cleaned_data['dockerIndexer'],
                             repo=form.cleaned_data['repo'],
                             tag=form.cleaned_data['tag'],
                             user=form.cleaned_data['user'],
                             uid=form.cleaned_data['uid'],
                             gid=form.cleaned_data['gid'],
                             supervisordUser=form.cleaned_data['supervisordUser'],
                             supervisordAutoRestart=form.cleaned_data['supervisordAutoRestart'],
                             supervisordAutoStart=form.cleaned_data['supervisordAutoStart'],
                             supervisordStartTimeSeconds=form.cleaned_data['supervisordStartTimeSeconds'],
                             extraPackages=map(lambda x: x.rstrip(), form.cleaned_data['extraPackages'].splitlines()),
                             sshKeysRoot=map(lambda x: x.rstrip(), form.cleaned_data['sshKeysRoot'].splitlines()),
                             sshKeysMinecraft=map(lambda x: x.rstrip(), form.cleaned_data['sshKeysMinecraft'].splitlines()),
                             firstName=form.cleaned_data['firstName'],
                             lastName=form.cleaned_data['lastName'],
                             email=form.cleaned_data['email'],
                             javaMaxMemMB=form.cleaned_data['javaMaxMemMB'],
                             javaInitMemMB=form.cleaned_data['javaInitMemMB'],
                             javaGCThreads=form.cleaned_data['javaGCThreads'],
                             )
            di.save()
            return redirect('DockerImageEdit', di._id)
    else:
        form = NewDockerInstanceForm()

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
                             _id=form.cleaned_data['itag'],
                             humanName=form.cleaned_data['humanName'],
                             humanDescription=form.cleaned_data['description'],
                             imageType='BaseImage',
                             imageID=None,
                             # TODO: Stop hard coding this
                             dockerParent='ubuntu:14.04',
                             dockerName=form.cleaned_data['dockerName'],
                             dockerIndexer=form.cleaned_data['dockerIndexer'],
                             repo=form.cleaned_data['repo'],
                             tag=form.cleaned_data['tag'],
                             proxy=form.cleaned_data['proxy'],
                             extraPackages=map(lambda x: x.rstrip(), form.cleaned_data['extraPackages'].splitlines()),
                             firstName=form.cleaned_data['firstName'],
                             lastName=form.cleaned_data['lastName'],
                             email=form.cleaned_data['email'],
                             )
            di.save()
            return redirect('DockerImageEdit', di._id)
    else:
        form = BaseDockerInstanceForm()

    return render_to_response(
                              'mcdocker/dockerMgmt/add.djhtml',
                              dict(
                                   form=form,
                                   ),
                              context_instance=RequestContext(req),
                              )



