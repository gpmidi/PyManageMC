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


# Ours
from mclogs.tasks import *


class WatchStreamThread(threading.Thread):
    """ Log the IO for the given stream
    """
    
    def __init__(self, stream, prg, name = 'Unnamed', loglevel = logging.INFO):
        threading.Thread.__init__(self)
        self.level = loglevel
        self.stream = stream
        self.prg = prg
        self.streamname = name
        self.setName(name = "WatchStreamThread-%s" % name)
        self.log = logging.getLogger("server.allServerTypes." + name)
        self.log.debug("Creating IO logger %r (%r)" % (name, self.getName()))
        self.setDaemon(False)
        
    def _logMessage(self,line):
        self.log.log(self.level, "Read: " + line)

        
    def run(self):
        rc = self.prg.poll()
        # TODO: This may result in the last few lines of logs being lost - Need to review
        while rc is None:
            line = self.stream.readline().rstrip('\n')
            if line != '' and line != '\n':
                self._logMessage(line = line)
            rc = self.prg.poll()
        line = self.stream.read()
        self.log.log(self.level, "Read: " + line)
        self.log.log(self.level, "-- Completed with a return code of %r --" % rc)
        

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'
    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action = 'store_true',
            dest = 'delete',
            default = False,
            help = 'Delete poll instead of closing it'),
        )

    def handle(self, *args, **options):
        prg = subprocess.Popen(args, stderr = subprocess.PIPE, stdout = subprocess.PIPE, cwd = cwd)
        for poll_id in args:
            try:
                poll = Poll.objects.get(pk = int(poll_id))
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write('Successfully closed poll "%s"' % poll_id)
    
