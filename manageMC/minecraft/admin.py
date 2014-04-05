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
from minecraft.models import *


# # admin.site.register(MinecraftServerCfgFile)
# admin.site.register(MapSave)
# # admin.site.register(PublicMapSave)
#
# class MinecraftServerCfgFileAdmin(admin.StackedInline):
#     model = MinecraftServerCfgFile
#     fields = ('cfgLoc',)
#     readonly_fields = ('serverInstance',)
#
#
# class MinecraftServerAdmin(admin.StackedInline):
#     model = MinecraftServer
#     fields = ('name', 'bin',)
#     readonly_fields = ('created', 'modified', 'instance',)
#     inlines = [
#                MinecraftServerCfgFileAdmin,
#                ]
#
#
# class MinecraftServerAdminMain(admin.ModelAdmin):
#     model = MinecraftServer
#     fields = ('name', 'bin',)
#     readonly_fields = ('created', 'modified', 'instance',)
#     inlines = [
#                MinecraftServerCfgFileAdmin,
#                ]
#
# admin.site.register(MinecraftServer, MinecraftServerAdminMain)
#
#
# admin.site.register(MinecraftServerBinary)
