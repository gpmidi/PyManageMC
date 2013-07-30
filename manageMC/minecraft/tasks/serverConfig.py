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
# Setup logging
import logging
log = logging.getLogger("minecraft.tasks.serverConfig")

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.files import File
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.template.loader import render_to_string

# Celery
from celery.task import task  # @UnresolvedImport

# Built-in

# Mcer
from minecraft.models import *
from minecraft.serverType import getServerFromModel, ServerProperitiesConfigFileType


@task(expires = 60 * 60)
def updateDB_MCConfig(configPK):
    """ Update the given server.properties config file  """
    mcp = MinecraftServerProperties.get(docid = configPK)

    mcServer = MinecraftServer.objects.get(pk = mcp.minecraftServerPK)
    # Get the class type that is the right type
    stype = getServerFromModel(mcServer = mcServer)
    # Server interaction object
    server = stype(mcServer = mcServer)
#     # Run the init
#     server.localInit()
    cfg = ServerProperitiesConfigFileType(
                                          serverDir = server.getServerRoot(),
                                          minecraftServerObj = server,
                                          )
    server.localUpdateConfigFile(cfg)
    
