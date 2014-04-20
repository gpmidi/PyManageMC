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
Created on Apr 5, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger('mclogs.tasks')

# Built-in
import os, os.path, sys  # @UnusedImport
import datetime, time  # @UnusedImport
import re

# External
from celery.task import task  # @UnresolvedImport
from celery.contrib.batches import Batches  # @UnresolvedImport
from django.conf import settings

# Ours
from minecraft.serverType import getServerFromModel
from minecraft.models import MinecraftServer


@task(expires=60 * 60 * 24 * 14)
def logLineAlert(**kwargs):
    """ Notify the admin via Django messages that a error/warn occurred """


@task(expires=60 * 60 * 24 * 14)
def logLineInfo(**kwargs):
    """ Notify the admin via Django messages that a error/warn/info occurred """


@task(expires=60 * 60 * 24 * 14)
def fetchSegment(serverId, length, offset=0, tail=True, ioType='stdout'):
    """ Fetch a segment of log files from the server's supervisord instance
    @return: dict(returnedBytes,newOffset=None,hasOverflow=None)
    """
    assert ioType in ['stdout', 'stdin']
    mcServer = MinecraftServer.get(serverId)
    serverType = getServerFromModel(mcServer)

    if serverType.supervisordState != 'RUNNING':
        raise RuntimeError(
           "The server %r(%r) is not running supervisord: Status=%r" % (
                  mcServer,
                  serverType,
                  serverType.supervisordState,
                  ))
    else:
        log.debug("Supervisord on %r is running", serverType)

    if tail:
        returnedBytes, newOffset, hasOverflow = serverType.tailMCLog(
                                                       offset=offset,
                                                       length=length,
                                                       ioType=ioType,
                                                       )
        return dict(
                   returnedBytes=returnedBytes,
                   newOffset=newOffset,
                   hasOverflow=hasOverflow,
                   )
    else:
        returnedBytes = serverType.readMCLog(
                                   offset=offset,
                                   length=length,
                                   ioType=ioType,
                                   )
        return dict(
                   returnedBytes=returnedBytes,
                   newOffset=None,
                   hasOverflow=None,
                   )


@task(expires=60 * 5)
def archiveAllLogs():
    """ Check all servers for any log files that have been rotated out
    @return: Number of log files loaded
    """
    for serverId in MinecraftServer.view('FIXME: fill this in'):
        archiveLogs.delay(serverId=serverId)


@task(expires=60 * 60)
def archiveLogs(serverId):
    """ Check the given server for any log files that have been rotated out
    @return: Number of log files loaded
    """
    server = MinecraftServer.get(serverId)
    serverType = getServerFromModel(server)
    count = 0

    if not serverType.isRunning:
        return count

    ids = serverType.archiveLogs()
    count += len(ids)

    log.debug("Archived %d log files", count)
    return count


#===============================================================================
# Below here currently unused
#===============================================================================
@task(expires=60 * 60 * 24 * 14)
def logLine(serverId, line, flow, whenReal=None, when=None, whenCaptured=None, **kwargs):
    if whenCaptured is None:
        whenCaptured = datetime.datetime.utcnow()

    kws = dict(
               serverId=serverId,
               line=line,
               message=line,
               source=None,
               flow=flow,
               # When the line was captured. May be fairly inaccurate.
               whenCaptured=whenCaptured,
               # Guaranteed to be accurate
               whenReal=whenReal,
               # Best guess as to when
               when=when,
               # Log priority level
               level=None,
               )
    for k, v in kwargs.items():
        kws[k] = v

    parsed = settings.PARSE_LOG_LINE.match(line)
    if parsed:
        d = parsed.groupdict()
        try:
            kws['whenReal'] = datetime.date.utcnow() + datetime.time(hour=int(d['hour']), minute=int(d['minute']), second=int(d['second']))
        except:
            pass
        if 'level' in d:
            kws['level'] = settings.MC_LOG_LEVELS.get(d['level'], None)
        if 'message' in d:
            kws['message'] = d['message']
        if 'source' in d:
            kws['source'] = d['source']

    if kws['whenReal']:
        kws['when'] = kws['whenReal']

    if kws['when'] is None:
        kws['when'] = kws['whenCaptured']

    ret = []
    if kws['level'] == 'WARN':
        ret.append(logLineAlert.delay(**kws))
    elif kws['level'] == 'ERROR':
        ret.append(logLineAlert.delay(**kws))

    ret.append(logLineInfo.delay(**kws))
    ret.append(aggLogLines.delay(**kws))
    return ret


@task(
      expires=60 * 60 * 24 * 14,
      base=Batches,
      flush_every=1024 * 128,
      flush_interval=60 * 5,
      )
def aggLogLines(requests):
    """ Accept log lines from one or more minecraft servers and then record them in CouchDB """
    linesByServer = {}
    for request in requests:
        args = request.args
        kw = request.kwargs
        serverId = kw.get('serverId', 'Unnamed')
        flow = kw.get('flow', 'Unnamed')
        line = kw.get('line', '').rstrip('\n')
        when = kw.get('when', None)

        if serverId not in linesByServer:
            linesByServer[serverId] = []
        linesByServer[serverId].append(dict(
                                            flow=flow,
                                            line=line,
                                            when=when,
                                            ))
    count = 0
    for serverId, lines in linesByServer.items():
        count += 1

