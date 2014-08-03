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

def index(req):
    """ Main page"""
    news = News.objects.filter(
                               published=True,
                               frontpage=True,
                               ).filter(
                                        modified__gt=datetime.datetime.now() - datetime.timedelta(days=7),
                                        ).order_by('-created')[:3]
    return render_to_response(
                              'index.html',
                              dict(
                                   news=news,
                                    ),
                              context_instance=RequestContext(req),
                              )
