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
import hashlib
import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.cache import cache
from django.utils.http import urlquote
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

from social.actions import do_auth, do_complete, do_disconnect  # @UnresolvedImport
from social.apps.django_app.utils import strategy  # @UnresolvedImport

from extern.models import *
from extern.forms import UserProfileForm


# User access
def userView(req, userPK = None):
    """ Show info about a particular user """
    if userPK is None and req.user.is_authenticated():
        user = req.user
    else:
        user = get_object_or_404(User, pk = userPK)
    return render_to_response(
                              'user.html',
                              dict(
                                   dUser = user,
                                   ),
                              context_instance = RequestContext(req),
                              )


# User access
def userLogin(req):
    """ Init login """
    return render_to_response(
                              'login.html',
                              dict(

                                   ),
                              context_instance = RequestContext(req),
                              )


@login_required
def userEditProfile(req):
    try:
        profile = req.user.get_profile()
    except ObjectDoesNotExist, e:
        profile = UserProfile(user = req.user)
        profile.save()
    
    if req.method == "POST":
        form = UserProfileForm(req.POST, instance = profile)
        if form.is_valid():
            req.user.first_name = form.cleaned_data['first_name']
            req.user.last_name = form.cleaned_data['last_name']
            # req.user.email = form.cleaned_data['email']
            req.user.save()
            form.save()
            messages.success(req, 'Profile details updated. ')
        else:
            messages.info(req, 'No changes made - Invalid data')
    else:
        form = UserProfileForm(initial = dict(
                                    first_name = req.user.first_name,
                                    last_name = req.user.last_name,
                                    # email = req.user.email,
                                    ),
                                instance = profile
                                )
    return render_to_response(
                              'profile_edit.html',
                              dict(
                                   form = form,
                                   ),
                              context_instance = RequestContext(req),
                              )
