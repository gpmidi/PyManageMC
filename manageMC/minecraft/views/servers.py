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
from mcer.minecraft.models import *
from mcer.minecraft.forms.EditServerForm import *

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
                
            for i in server.plugins:
                if not i in m.plugins:
                    # Remove a plugin
            for i in m.plugins:
                if not i in server.plugins:
                    # Add a plugin
            
            if m.owner.pk != server.owner.pk:
                # Chagne owning group
                pass
            
            if m.listen != server.listen or m.port != server.port:
                # Change server listening info
                
            if m.auto_save != server.auto_save:
                # Change auto save
            
            
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
    
    return render_to_response(
                              'mcer/servers/new.html',
                              dict(
                                    ),
                              context_instance = RequestContext(req),
                              )
    
    
    

