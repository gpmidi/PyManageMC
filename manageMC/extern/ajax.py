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
from django.template.loader import render_to_string
from django.db.models import Q
from django.http import Http404
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import os.path
from mimetypes import guess_type
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import permission_required, login_required
from dajaxice.core import dajaxice_functions  # @UnresolvedImport

from minecraft.models import *
from minecraft.tasks.server import *


@login_required
@permission_required('extern.make_serverinstance_managed')
def change_serverinstance(req, server_pk):
    """ Run a raw command on a server """
    raise NotImplementedError("FIXME: Fill in make managed")
    dajax = Dajax()
    # dajax.prepend('#adminActionLog', 'innerHTML', 'Running "%s"\n' % cmd)
    dajax.prepend('#messageList', 'innerHTML', '')
    return dajax.json()

dajaxice_functions.register(change_serverinstance)
