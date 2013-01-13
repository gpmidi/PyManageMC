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

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # /
    url(r'^(?:/)?$', 'extern.views.index'),
    
    # General interaction
    url(r'^e/', include('extern.urls')),
    
    # User
    url(r'^accounts/login(?:/)?$', 'django.contrib.auth.views.login',),
    url(r'^accounts/profile(?:/)?$', 'extern.views.userEditProfile', name = "UserProfileEdit"),
    url(r'^accounts/password/change(?:/)?$', 'django.contrib.auth.views.password_change', name = "UserChangePassword"),
    url(r'^accounts/password/done(?:/)?$', 'django.contrib.auth.views.password_change_done', name = "UserChangePasswordDone"),
    url(r'^accounts/logout(?:/)?$', 'django.contrib.auth.views.logout_then_login', name = "UserLogout"),
    url(r'^accounts/reset(?:/)?$', 'django.contrib.auth.views.password_reset', name = "UserResetPassword"),
    url(r'^accounts/reset/done(?:/)?$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)(?:/)?$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^accounts/reset/done(?:/)?$', 'django.contrib.auth.views.password_reset_complete'),
    
    # Admin
    url(r'^admin/', include(admin.site.urls)),
)
