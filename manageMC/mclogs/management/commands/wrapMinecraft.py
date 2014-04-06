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
log = logging.getLogger('mclogs.management.commands.wrapMinecraft')

# Built-in
import os,os.path,sys
import threading
from optparse import make_option
import subprocess

# External
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import caches  # @UnresolvedImport

# Ours
from mclogs.tasks import *
from mclogs.models import *


class WatchStreamThread(threading.Thread):
    """ Log the IO for the given stream
    """
    
    def __init__(self, serverId, stream, prg, streamType, name = 'Unnamed', loglevel = logging.INFO):
        threading.Thread.__init__(self)
        self.streamType = streamType
        self.level = loglevel
        self.serverId=serverId
        self.stream = stream
        self.prg = prg
        self.streamname = name
        self.setName(name = "WatchStreamThread-%s" % name)
        self.log = logging.getLogger("server.allServerTypes." + name)
        self.log.debug("Creating IO logger %r (%r)" % (name, self.getName()))
        self.setDaemon(False)
        self.lastTen = []
        
    def _logMessage(self, line):
        self.log.log(self.level, "Read: " + line)
        self.lastTen.append(line)
        if len(self.lastTen) > 10:
            self.lastTen.pop(0)
        logLine.delay(
                      serverId = self.serverId,
                      line=line, 
                      flow=self.streamname,
                      whenCaptured = datetime.datetime.now(), 
                      streamType = self.streamType,
                      )
        caches['status'].set(
                             'SERVER-%s-RECENT' % self.serverId,
                             '\n'.join(self.lastTen),
                             60 * 60 * 24 * 14,
                             )
        
    def run(self):
        rc = self.prg.poll()
        while rc is None:
            line = self.stream.readline().rstrip('\n')
            if line != '' and line != '\n':
                self._logMessage(line = line)
            rc = self.prg.poll()
        time.sleep(5)
        for line in self.stream.read().splitlines():
            self._logMessage(line = line)
        self.log.log(self.level, "-- Completed with a return code of %r --" % rc)
        

class Command(BaseCommand):
    args = '<cmd args>'
    help = 'Start an MC server'
    option_list = BaseCommand.option_list + (
        make_option('--serverId',
            action = 'store',
            dest = 'serverId',
            default = None,
            help = 'Server ID'),
        )

    def handle(self, *args, **opts):
        prg = subprocess.Popen(
                               args = args,
                               stderr = subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               cwd = os.getcwd(),
                               )
        stderr = WatchStreamThread(
                                   serverId = opts.serverId,
                                   stream=prg.stderr,
                                   prg=prg,
                                   name='%s.stderr'%args[0],
                                   streamType = 'STDERR',
                                   )
        stderr.start()
        stdout = WatchStreamThread(
                                   serverId = opts.serverId,
                                   stream = prg.stdout,
                                   prg = prg,
                                   name = '%s.stdout' % args[0],
                                   streamType = 'STDOUT',
                                   )
        stdout.start()
        
        rc = prg.poll()
        while rc is None:
            caches['status'].set(
                                 'SERVER-%s-STATUS' % opts.serverId,
                                 'RUNNING',
                                 60 * 60 * 24 * 14,
                                 )
            caches['status'].set(
                                 'SERVER-%s-PID' % opts.serverId,
                                 str(prg.pid),
                                 60 * 60 * 24 * 14,
                                 )
            time.sleep(1)
            rc = prg.poll()

        caches['status'].set(
                             'SERVER-%s-STATUS' % opts.serverId,
                             'ENDED-WITH-%d' % rc,
                             60 * 60 * 24 * 14,
                             )
        caches['status'].set(
                             'SERVER-%s-PID' % opts.serverId,
                             None,
                             60 * 60 * 24 * 14,
                             )



            





