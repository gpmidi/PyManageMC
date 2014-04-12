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
log = logging.getLogger('minecraft.views.index')

# Built-in
import os, os.path, sys  # @UnusedImport

# External
from django.core.exceptions import ObjectDoesNotExist  # @UnusedImport
from django.shortcuts import render_to_response, get_object_or_404, render  # @UnusedImport
from django.db.models import Q  # @UnusedImport
from django.template import RequestContext  # @UnusedImport
from django.contrib.auth.models import AnonymousUser  # @UnusedImport
from django.views.decorators.cache import cache_page  # @UnusedImport
from django.core.paginator import Paginator, EmptyPage, InvalidPage  # @UnusedImport

# Ours
from minecraft.models import *  # @UnusedWildImport
from mcdocker.models import *  # @UnusedWildImport
from mcdocker.tasks import *  # @UnusedWildImport



def index(req):
    """ Main index """
    return render_to_response(
                              'mcer/index.html',
                              dict(
                                    ),
                              context_instance=RequestContext(req),
                              )
