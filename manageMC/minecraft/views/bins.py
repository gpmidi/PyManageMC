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
# Built-in

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from couchdbkit.exceptions import ResourceNotFound

# Mcer
from minecraft.models import *
from minecraft.forms.EditServerForm import *
from extern.models import *


@login_required
@permission_required('minecraft.change_serverinstance')
def index(req):  #
    """ List all of binaries """
    bins = MinecraftServerBinary.view('minecraft/binariesByStatus')
    return render_to_response(
                              'bins/index.html',
                              dict(
                                   bins = bins,
                                   ),
                              context_instance = RequestContext(req),
                              )
    

@login_required
@permission_required('minecraft.change_serverinstance')
def view(req, binId):
    """ View a binary """
    try:
        binObj = MinecraftServerBinary.get(binId)
    except ResourceNotFound as e:
        raise Http404("Binary not found")

    return render_to_response(
                              'bins/view.html',
                              dict(
                                   binObj = binObj,
                                   ),
                              context_instance = RequestContext(req),
                              )


# @login_required
# @permission_required('minecraft.change_serverinstance')
# def edit(req, instanceName):
#     """ View/Edit a server """
#     server = get_object_or_404(MinecraftServer, _id = instanceName)
#     if not server.checkUser(req = req, perms = 'admin'):
#         raise Http404()
#
#     if req.POST:
#         form = EditServerForm(req.POST, instance = server)
#         if form.is_valid():
#             m = form.save(commit = True)
#             if server.bin.pk != m.bin.pk:
#                 # Change the server exec
#                 server.bin = m.bin
#                 server.save()
#             server = m
#         else:
#             pass
#     else:
#         form = EditServerForm(instance = server)
#
#     return render_to_response(
#                               'servers/edit.html',
#                               dict(
#                                    server = server,
#                                    instance = server.getInstance(),
#                                    form = form,
#                                    ),
#                               context_instance = RequestContext(req),
#                               )


    
# @login_required
# @permission_required('minecraft.add_serverinstance')
# def newserver(req):
#     """ Create a server """
#
#     raise NotImplementedError("FIXME: Finish this")
#
#     return render_to_response(
#                               'servers/new.html',
#                               dict(
#                                     ),
#                               context_instance = RequestContext(req),
#                               )
    
    
    

