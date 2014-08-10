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
log = logging.getLogger('mcdocker.urls')

# Built-in
import os, os.path, sys  # @UnusedImport

# External
from django.conf.urls import patterns, include, url

# Ours


urlpatterns = patterns('mcdocker.views',  # /mcOS/...
    url(r'^images/$', 'dockerImageIndex', name='DockerImageIndex'),
    url(r'^image/([a-zA-Z0-9_\-]+)/$', 'dockerImageEdit', name='DockerImageEdit'),
    url(r'^image/([a-zA-Z0-9_\-]+)/build/$', 'dockerImageBuild', name='DockerImageBuild'),
    url(r'^newimage/$', 'dockerImageCreate', name='DockerImageCreate'),
    url(r'^newbaseimage/$', 'dockerBaseImageCreate', name='DockerBaseImageCreate'),
)
