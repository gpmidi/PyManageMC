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
from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('minecraft.views',
    # Server access
    url(r'^servers(?:/)?$', 'servers.index'),
    # url(r'^server/new(?:/)?$', 'servers.newserver'),
    url(r'^servers/(?P<serverSlug>[a-zA-Z0-9\-_]+)(?:/)?$', 'servers.view'),
    # url(r'^servers/(\d+)/edit(?:/)?$', 'servers.edit'),

    url(r'^bins/new/upload(?:/)?$', 'bins.uploadNew'),
    url(r'^bins/new/byURL(?:/)?$', 'bins.dlNew'),
    url(r'^bins/new/search(?:/)?$', 'bins.searchNew'),
    url(r'^bins(?:/)?$', 'bins.index'),
    url(r'^bins/(?P<binId>[a-zA-Z0-9\-_]+)(?:/)?$', 'bins.view'),
)
