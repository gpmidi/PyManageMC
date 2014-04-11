#!/usr/bin/python
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
Created on Apr 11, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger('mcdocker.tasks')

# Built-in
import os, os.path, sys  # @UnusedImport
from StringIO import StringIO
import tarfile

# External
from celery.task import task  # @UnresolvedImport
import docker
from django.conf import settings
from django.template.loader import render_to_string

# Ours
from mcdocker.models import *  # @UnusedWildImport


def getClient():
    """ Return a new docker API client """
    return docker.Client(
                         base_url=settings.DOCKER_BASE_URL,
                         version=settings.DOCKER_VERSION,
                         timeout=settings.DOCKER_TIMEOUT,
                         )


def addFile(tf, filename, template, context):
    rs = render_to_string(template, context,)

    tarInfo = tarfile.TarInfo(filename)
    tarInfo.size = len(rs)
    tarInfo.mode = 0700
    tarInfo.uid = 0
    tarInfo.gid = 0

    newFile = StringIO()
    newFile.write(rs)

    tf.addfile(tarInfo, newFile)


@task(expires=60 * 60)
def buildImage(dockerImageID):
    di = DockerImage.get(dockerImageID)
    if di.imageType == 'BaseImage':
        templateName = '00-MCBase.Dockerfile'
    elif di.imageType == 'UserImage':
        templateName = '10-MC.Dockerfile'
    else:
        raise ValueError("%r is not a valid docker image type" % di.imageType)

    tarFile = StringIO()
    tf = tarfile.open(mode='w:gz', fileobj=tarFile)

    addFile(
            tf=tf,
            filename="/Dockerfile",
            template="/mcdocker/dockerFiles/" + templateName,
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/logrotate.d/supervisord.conf",
            template="/mcdocker/configs/logrotate.d/supervisord.conf",
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/supervisord.d/cron.conf",
            template="/mcdocker/configs/supervisord.d/cron.conf",
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/supervisord.d/minecraft.conf",
            template="/mcdocker/configs/supervisord.d/minecraft.conf",
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/supervisord.d/sshd.conf",
            template="/mcdocker/configs/supervisord.d/sshd.conf",
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/minecraft.authorized_keys",
            template="/mcdocker/configs/minecraft.authorized_keys",
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/root.authorized_keys",
            template="/mcdocker/configs/root.authorized_keys",
            context=dict(image=di),
            )
    addFile(
            tf=tf,
            filename="/supervisord.conf",
            template="/mcdocker/configs/supervisord.conf",
            context=dict(image=di),
            )

    tf.close()

    client = getClient()

    image, logs = client.build(
                 path=None,
                 tag=di.getFullDockerName(),
                 quiet=True,
                 fileobj=tarFile,
                 nocache=False,
                 rm=False,
                 stream=False,
                 )

    log.debug("Built image %r", image)
    log.debug("Logs for %r: %r", image, logs)

    return image











