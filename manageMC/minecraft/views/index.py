# Django
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, InvalidPage

# Built-in

# Mcer
from mcer.minecraft.models import *

def index(req):
    """ Main index """
    return render_to_response(
                              'mcer/index.html',
                              dict(
                                    ),
                              context_instance = RequestContext(req),
                              )
