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
import urllib
import itertools

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404, redirect
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
from minecraft.forms.binaries import *
from extern.models import *


@login_required
@permission_required('minecraft.upload_minecraftserverbinary')
def uploadNew(req):
    """ Upload a new server binary """
    if req.method == 'POST':
        form = UploadBinaryForm(req.POST, req.FILES)
        if form.is_valid():
            # FIXME: Catch errors here
            doc = MinecraftServerBinary()
            doc.typeName = form.cleaned_data['typeName']
            doc.version = form.cleaned_data['version']
            doc.releaseStatus = form.cleaned_data['releaseStatus']
            doc.save()
            doc.put_attachment(
                               name = 'binary',
                               content = req.FILES['binary'],
                               )
            if 'helperFiles' in req.FILES:
                doc.put_attachment(
                               name = 'helperFiles',
                               content = req.FILES['helperFiles'],
                               )
            if 'helperFilesConfig' in req.FILES:
                doc.put_attachment(
                               name = 'helperFilesConfig',
                               content = req.FILES['helperFilesConfig'],
                               )
            doc.save()
            return redirect('/mc/bins/%s/' % urllib.quote(doc._id))
    else:
        form = UploadBinaryForm()
    return render_to_response(
                              'bins/uploadNew.html',
                              dict(
                                   form = form,
                                   ),
                              context_instance = RequestContext(req),
                              )


@login_required
@permission_required('minecraft.search_minecraftserverbinary')
def searchNew(req):
    """ Search new server binaries """
    raise NotImplementedError()
    return render_to_response(
                              'bins/index.html',
                              dict(
                                   ),
                              context_instance = RequestContext(req),
                              )


@login_required
@permission_required('minecraft.download_minecraftserverbinary')
def dlNew(req):
    """ Download a new server binary from a given URL """
    raise NotImplementedError()
    return render_to_response(
                              'bins/index.html',
                              dict(
                                   ),
                              context_instance = RequestContext(req),
                              )


@login_required
@permission_required('minecraft.change_serverinstance')
def index(req):  #
    """ List all of binaries """
    bins = list(MinecraftServerBinary.view('minecraft/binariesAll'))
    gBy = {}
    for typeName, v in itertools.groupby(bins, lambda x: (x['key'][0],)):
        gBy[typeName] = {}
        for releaseStatus, v2 in itertools.groupby(v, lambda x: (x['key'][1],)):
            gBy[typeName][releaseStatus] = list(v2)
    return render_to_response(
                              'bins/index.html',
                              dict(
                                   gBy = gBy,
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

    import base64
    import binascii
    def convHash(hsh):
        htype, hsh = hsh.split('-')
        hx = binascii.hexlify(base64.b64decode(hsh))
        return (htype.upper(), hx)

    return render_to_response(
                              'bins/view.html',
                              dict(
                                   binObj = binObj,
                                   binObjId = binId,
                                   binary = lambda: 'binary' in binObj._attachments,
                                   binaryHash = lambda: convHash(binObj._attachments['binary']['digest']),
                                   binaryLength = lambda: binObj._attachments['binary']['length'],
                                   helper = lambda: 'helperFiles' in binObj._attachments,
                                   helperHash = lambda: convHash(binObj._attachments['helperFiles']['digest']),
                                   helperLength = lambda: binObj._attachments['helperFiles']['length'],
                                   helperCfg = lambda: 'helperFilesConfig' in binObj._attachments,
                                   helperCfgHash = lambda: convHash(binObj._attachments['helperFilesConfig']['digest']),
                                   helperCfgLength = lambda: binObj._attachments['helperFilesConfig']['length'],
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
    
    
    

