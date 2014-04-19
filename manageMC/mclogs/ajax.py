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
Created on Apr 19, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from dajax.core import Dajax  # @UnresolvedImport
from dajaxice.decorators import dajaxice_register  # @UnresolvedImport
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
from django.contrib.auth.decorators import login_required
import json

from minecraft.models import *
from minecraft.tasks.server import *


@dajaxice_register
@login_required
def fetchLogSegment(req, serverId, length, offset=0, tail=True, ioType='stdout'):
    """ Fetch log segment """
    try:
        serverId = str(serverId)
        length = int(length)
        offset = int(offset)
        tail = bool(tail)

        assert ioType in ['stdout', 'stderr'], "Invalid IO type %r" % ioType
        assert length > 50 and length < 1024 * 1024, "Length is out of range"
        assert offset >= 0 and offset <= 1024 * 1024 * 1024, "Offset is out of range"

        server = MinecraftServer.get(str(serverId))
    except Exception as e:
        log.exception("Failed to parse args for fetchLogSegment with %r", e)
        return json.dumps(dict(
                               success=False,
                               ))

    from mclogs.tasks import fetchSegment
    res = fetchSegment.delay(# @UndefinedVariable
                             serverId=server._id,
                             length=length,
                             offset=offset,
                             tail=tail,
                             ioType=ioType,
                             ).get()  # @UndefinedVariable

    returnedBytes = res['returnedBytes']
    newOffset = res['newOffset']
    hasOverflow = res['hasOverflow']

    lines = []
    for line in returnedBytes.splitlines():
        lines.append(line)

    ret = dict(
             success=True,
             lines=lines,
             newOffset=newOffset,
             hasOverflow=hasOverflow,
             )

    if returnedBytes[-1] != '\n':
        ret['partial'] = lines.pop()

    return json.dumps(ret)

