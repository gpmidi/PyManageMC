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
'''
Created on Feb 16, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django.contrib import admin
from extern.models import *


class NewsAdmin(admin.ModelAdmin):
    list_filter = (
                   'published',
                   'frontpage',
                   )
    list_display = (
                  'title',
                  'published',
                  'frontpage',
                  'created',
                  'modified',
                  )
    ordering = (
                '-created',
                )

admin.site.register(News, NewsAdmin)


class ExtraUserEmailInline(admin.TabularInline):
    model = ExtraUserEmail
    extra = 0


class MinecraftUsernameInline(admin.TabularInline):
    model = MinecraftUsername
    extra = 0


class UserPhoneNumberInline(admin.TabularInline):
    model = UserPhoneNumber
    extra = 0


class ServerSystemIPsInline(admin.TabularInline):
    model = ServerSystemIPs


class UserProfileAdmin(admin.ModelAdmin):
    inlines = [
        MinecraftUsernameInline,
        ExtraUserEmailInline,
        UserPhoneNumberInline,
    ]

admin.site.register(UserProfile, UserProfileAdmin)


class ServerSystemAdmin(admin.ModelAdmin):
    inlines = [
               ServerSystemIPsInline,
    ]

admin.site.register(ServerSystem, ServerSystemAdmin)


class ServerInstanceExternalInfoInline(admin.TabularInline):
    model = ServerInstanceExternalInfo


class ServerInstanceAdmin(admin.ModelAdmin):
    inlines = [
        ServerInstanceExternalInfoInline,
#        MinecraftServerAdmin,
    ]

admin.site.register(ServerInstance, ServerInstanceAdmin)
