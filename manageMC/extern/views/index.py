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
                               published = True,
                               frontpage = True,
                               ).filter(
                                        modified__gt = datetime.datetime.now() - datetime.timedelta(days = 7),
                                        ).order_by('-created')[:3]
    return render_to_response(
                              'index.html',
                              dict(
                                   news = news,
                                    ),
                              context_instance = RequestContext(req),
                              )
