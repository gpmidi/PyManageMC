'''
Created on Jan 12, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.models import User, Group

import datetime

from extern.models import *

# User access
def userView(req, userPK):
    """ Show info about a particular user """
    user = get_object_or_404(User, pk = userPK)
    return render_to_response(
                              'user.html',
                              dict(
                                   dUser = user,
                                   ),
                              context_instance = RequestContext(req),
                              )
