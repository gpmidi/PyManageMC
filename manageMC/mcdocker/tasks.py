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
import xmlrpclib
import tempfile

# External
from celery.task import task  # @UnresolvedImport
from celery.result import AsyncResult  # @UnresolvedImport
import docker
from django.conf import settings  # @UnusedImport
from django.template.loader import render_to_string
from couchdbkit.exceptions import ResourceNotFound  # @UnusedImport

# Ours
from mcdocker.models import *  # @UnusedWildImport
from minecraft.models import *  # @UnusedWildImport


def getClient():
    """ Return a new docker API client """
    return docker.Client(
                         base_url=settings.DOCKER_BASE_URL,
                         version=settings.DOCKER_VERSION,
                         timeout=settings.DOCKER_TIMEOUT,
                         )


def addFile(tf, filename, template, context):
    log.debug("Going to render %r", template)
    rs = render_to_string(template, context,)

    newFile = StringIO()
    newFile.write(rs)

    tarInfo = tarfile.TarInfo(filename)
    tarInfo.size = len(rs)
    tarInfo.mode = 0700
    tarInfo.uid = 0
    tarInfo.gid = 0
    tarInfo.name = filename
    newFile.name = filename

    newFile.seek(0)

    tf.addfile(tarInfo, newFile)


@task(expires=60 * 60 * 24 * 7 * 6)  # 6 weeks
def doBuildImageError(uuid, dockerImageId):
    log.debug(
              "Build task %r for image %r failed",
              uuid,
              dockerImageId,
              )
    di = DockerImage.get(dockerImageId)
    di.buildStatus = 'Failed'
    di.save()


def doBuildImage(di):
    """ Shortcut to kicking off a build """
    dockerImageId = di._id

    if di.buildStatus not in ['NotStarted', 'Failed']:
        raise ValueError("%r is not a valid build status to start a build from" % di.buildStatus)

    di.buildStatus = 'Started'
    di.save()

    errorh = doBuildImageError.s(dockerImageId=dockerImageId)
    job = buildImage.apply_async(
                                 (di._id,),
                                 link_error=errorh,
                                 )
    log.debug("Started build %r for %r", job, di._id)
    return job


RE_MATCH_BUILD_OK = re.compile(r'.*Successfully built ([0-9a-f]+)', re.DOTALL)

@task(expires=60 * 60)
def buildImage(dockerImageID):
    di = DockerImage.get(dockerImageID)
    di.buildStatus = 'InProgress'
    di.save()

    if di.imageType == 'BaseImage':
        templateName = '00-MCBase.Dockerfile'
    elif di.imageType == 'UserImage':
        templateName = '10-MC.Dockerfile'
    else:
        raise ValueError("%r is not a valid docker image type" % di.imageType)

    with tempfile.TemporaryFile(
                                mode='w+b',
                                prefix='buildImage-',
                                suffix='.tmp',
                                ) as tarFile:
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

        log.debug("Done adding files")
        tf.close()
        tarFile.seek(0)

        log.debug("Setting up docker client")
        client = getClient()

        log.debug("Starting docker build")
        res = client.build(
                     path=None,
                     tag=di.getFullDockerName(),
                     quiet=False,
                     fileobj=tarFile,
                     nocache=False,
                     rm=False,
                     stream=False,
                     custom_context=True,
                     encoding='gzip',
                     )
        logs = ''
        image = None
        for line in res:
            try:
                d = json.loads(line)
                if 'stream' in d:
                    log.debug("IO: %s", d['stream'].rstrip())
                    logs += d['stream']
                    m = RE_MATCH_BUILD_OK.match(d['stream'])
                    if m:
                        image = m.group(1)
                else:
                    log.debug("IO: %r", line.rstrip())
            except Exception, e:
                log.exception("IO: %r", line.rstrip())

        if image is None:
            log.warn("Failed to build %r", di._id)
        else:
            log.debug("Built image %r", image)

        di.buildStatus = 'Done'
        di.imageID = image
        di.save()

        return image


@task(expires=60 * 60 * 24)
def inspectDockerContainer(containerID, client=None):
    log.debug("Inspecting docker container %r", containerID)
    assert containerID, 'Expected containerID %r to be valid' % containerID
    if client is None:
        client = getClient()
    return client.inspect_image(containerID)


@task(expires=60 * 60 * 24)
def inspectDockerImage(imageID, client=None):
    log.debug("Inspecting docker image %r", imageID)
    assert imageID, 'Expected imageID %r to be valid' % imageID
    if client is None:
        client = getClient()
    return client.inspect_image(imageID)


@task(expires=60 * 60 * 24)
def getRealVolumeLocation(containerID, dockerImageId, volumeId, client=None):
    image = DockerImage.get(dockerImageId)

    if client is None:
        client = getClient()

    volume = image.volumes[volumeId]

    containerInfo = inspectDockerContainer(containerID, client)

    return containerInfo['Volumes'][volume]


@task(expires=60 * 60 * 4)
def createStartContainer(serverId, client=None):
    server = MinecraftServer.get(serverId)
    image = server.getImage()
    instance = server.getInstance()  # @UnusedVariable

    assert image.imageType == 'UserImage', "Expected a user image"

    if client is None:
        client = getClient()

    # Always make the Minecraft port accessible
    # pb[str(settings.MINECRAFT_DEFAULT_PORT_CONTAINER)] = (instance.internalIP, instance.port)
    log.debug("Port mappings set to %r", image.ports)


    # FIXME: Add in MORE ENV variables with other useful info for inside the container
    env = {
         'MINECRAFT_PORT_INT':str(settings.MINECRAFT_DEFAULT_PORT_CONTAINER),
         'SSH_PORT_INT':str(settings.MINECRAFT_DEFAULT_PORT_SSH),
         'SUPVD_PORT_INT':str(settings.MINECRAFT_DEFAULT_PORT_SUPVD),
         'MINECRAFT_RCON_PORT_INT':str(settings.MINECRAFT_DEFAULT_PORT_RCON),
         }
    if image.proxy:
        env['http_proxy'] = image.proxy
    log.debug("Env for system set to %r", env)


    # Create the container
    log.debug("Going to create container %r named %r", image.imageID, server.name)
    kw = dict(image=image.imageID,
                            detach=True,
                            mem_limit="%dm" % image.dockerMemoryLimitMB,
                            hostname=image.name,
                            dns=None,
                            cpu_shares=image.dockerCPUShare,
                            name=server.name,
                            environment=env,
                            command="/usr/bin/supervisord --nodaemon --logfile=/var/log/supervisord.log --loglevel=warn --logfile_maxbytes=1GB --logfile_backups=0",
                            user=None,
                            ports=image.ports.keys(),
                            volumes=server.getImage().volumes.values(),
                            stdin_open=False,
                            tty=False,
                            volumes_from=None,
                            network_disabled=False,
                            entrypoint=None,
                            working_dir=None,)
    log.warn("Running with %r", kw)
    results = client.create_container(
                            **kw
                            )
    log.debug("Results: %r", results)

    log.debug("Going to start %r", server.name)
    results = client.start(
                           server.name,
                           binds=server.getVolumeLocations(),
                           port_bindings=image.ports,
                           publish_all_ports=True,
                           links=None,
                           privileged=False,
                           )
    log.debug("Results: %r", results)

    return server.name

