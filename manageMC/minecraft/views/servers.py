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
# Django
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required

# Built-in

# Mcer
from minecraft.models import *
from minecraft.forms.EditServerForm import *

@login_required
def index(req):
    """ List all of my servers """
    servers = MinecraftServer.objects.filter(owner__in = req.user.groups.all())
    return render_to_response(
                              'mcer/servers/index.html',
                              dict(
                                   servers = servers,
                                    ),
                              context_instance = RequestContext(req),
                              )
    
@login_required
def view(req, server_id):
    """ View/Edit a server """
    server = get_object_or_404(MinecraftServer, pk = server_id)
    
    if req.POST:
        form = EditServerForm(req.POST)
        if form.is_valid():
            m = form.save(commit = True)
            if server.bin.pk != m.bin.pk:
                # Change the server exec
                server.bin = m.bin
                server.save()
            for i in server.plugins:
                if not i in m.plugins:
                    # Remove a plugin
                    raise NotImplementedError("FIXME: Need to add support for removing plugins")
            for i in m.plugins:
                if not i in server.plugins:
                    # Add a plugin
                    raise NotImplementedError("FIXME: Need to add support for adding plugins")
            if m.owner.pk != server.owner.pk:
                # Chagne owning group
                raise NotImplementedError("FIXME: Need to add support for changing owners")
            
            if m.listen != server.listen or m.port != server.port:
                # Change server listening info
                raise NotImplementedError("FIXME: Need to add support for changing the server's port")
            if m.auto_save != server.auto_save:
                # Change auto save
                raise NotImplementedError("FIXME: Need to add support for changing the server's auto-save policy")            
            server = m
        else:
            pass
    else:
        form = EditServerForm()
    
    return render_to_response(
                              'mcer/servers/view.html',
                              dict(
                                   server = server,
                                   form = form,
                                    ),
                              context_instance = RequestContext(req),
                              )
    
    
@login_required
def newserver(req):
    """ Create a server """
    
    raise NotImplementedError("FIXME: Finish this")

    return render_to_response(
                              'mcer/servers/new.html',
                              dict(
                                    ),
                              context_instance = RequestContext(req),
                              )
    
    
    

