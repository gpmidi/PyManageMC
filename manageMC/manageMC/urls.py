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
# Dajax
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()
# Admin
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Keep first - Will be heavily used eventually
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    # Auth
    url('', include('social.apps.django_app.urls', namespace = 'social')),
    # /
    url(r'^(?:/)?$', 'extern.views.index'),
    url(r'^index(?:\.html)?(?:/)?$', 'extern.views.index'),
    
    # General interaction
    url(r'^e/', include('extern.urls')),
    url(r'^mc/', include('minecraft.urls')),

    # User
    url(r'^accounts/login(?:/)?$', 'extern.views.userLogin', name = 'UserLogin'),
    url(r'^accounts/profile(?:/)?$', 'extern.views.userEditProfile', name = "UserProfileEdit"),
    url(r'^accounts/self(?:/)?$', 'extern.views.userView', name = "UserSelf"),
#     url(r'^accounts/password/change(?:/)?$', 'django.contrib.auth.views.password_change', name = "password_change"),
#     url(r'^accounts/password/done(?:/)?$', 'django.contrib.auth.views.password_change_done', name = "password_change_done"),
#     url(r'^accounts/logout(?:/)?$', 'django.contrib.auth.views.logout_then_login', name = "logout_then_login"),
#     url(r'^accounts/reset(?:/)?$', 'django.contrib.auth.views.password_reset', name = "password_reset"),
#     url(r'^accounts/reset/done(?:/)?$', 'django.contrib.auth.views.password_reset_done', name = 'password_reset_done'),
#     url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)(?:/)?$', 'django.contrib.auth.views.password_reset_confirm', name = 'password_reset_confirm'),
#     url(r'^accounts/reset/done(?:/)?$', 'django.contrib.auth.views.password_reset_complete', name = 'password_reset_complete'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
