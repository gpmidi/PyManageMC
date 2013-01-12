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

urlpatterns = patterns('manageMC.extern.urls',
    url(r'^(?:/)?$', 'index'),
    # Server instances
    url(r'^instances(?:/)?$', 'instances'),
    url(r'^instances/([a-zA-Z0-9\-_]+)(?:/)?$', 'instance'),
)