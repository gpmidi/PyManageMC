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
''' A type of server such as "stock" or "bukkit". 
Created on Aug 11, 2012

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Setup logging
import logging
log = logging.getLogger("server.allServerTypes." + __name__)

import subprocess
import re
from minecraft.models import *

allServerTypes = {}

fileTypeRegister = {}
    
class _fileType(type):
    def __init__(cls, name, bases, dct):
        super(_fileType, cls).__init__(name, bases, dct)
        if cls.SERVERTYPE:
            if not fileTypeRegister.has_key(cls.SERVERTYPE):
                fileTypeRegister[cls.SERVERTYPE] = {}
            # print "Setting %r to %r.%r already has %r" % (typ,cls.SERVERTYPE, name, cls)
            assert not fileTypeRegister[cls.SERVERTYPE].has_key(name), "Error: %r.%r already has %r" % (cls.SERVERTYPE, name, cls)
            fileTypeRegister[cls.SERVERTYPE][name] = cls

class FileType(object):
    __metaclass__ = _fileType
    """ Represent a type of file and how to handle it 
    when installing/upgrading/modifying
    """
    # ServerType TYPE value
    SERVERTYPE = None
    
    # The file may be changed by something other than this code
    MAY_EXTERNAL_UPDATE = False 
    
    # Overwrite on dup
    OVERWRITE = None
    
    # Regex used to match the file. May not be needed if matchFile is overridden. 
    # Must be a compiled regex
    FILE_MATCH = None
    
    def matchFile(self, filePath):
        """ filePath should be relative to the base of the server
        directory. 
        """
        assert filePath[0] != '/'
        return self.FILE_MATCH.match(filePath)

        
class OverwriteFileType(FileType):
    """ A file that should be overwritten whenever an update
    occurs """
    OVERWRITE = True


class NoOverwriteFileType(FileType):
    """ A file that should not be overwritten whenever an update
    occurs """
    OVERWRITE = False

    
class ConfigFileType(NoOverwriteFileType):
    """ A special type of file that should never be overwritten 
    but may be modified by the user. May also be automatically 
    updated by the server process
    """


class _serverTypeType(type):
    def __init__(cls, name, bases, dct):
        super(_serverTypeType, cls).__init__(name, bases, dct)
        # Skip any where TYPE is none, such as the base class
        if cls.TYPE:
            # Make sure no type ids are duplicated
            assert not allServerTypes.has_key(cls.TYPE)
            allServerTypes[cls.TYPE] = cls


import threading
class _IOLoggerThread(threading.Thread):
    
    def __init__(self, stream, prg, name = 'Unnamed', loglevel = 20):
        threading.Thread.__init__(self)
        self.level = loglevel
        self.stream = stream
        self.prg = prg
        self.streamname = name
        self.setName(name = "IOReaderThread-%s" % name)
        self.log = logging.getLogger("server.allServerTypes." + name)
        self.log.debug("Creating IO logger %r (%r)" % (name, self.getName()))
        self.setDaemon(True)
        
    def run(self):
        rc = self.prg.poll()
        while rc is None:
            line = self.stream.readline()
            self.log.log(self.level, "Read: " + line)            
            rc = self.prg.poll()
        line = self.stream.readline()
        self.log.log(self.level, "Read: " + line)
        self.log.log(self.level, "--Completed with a return code of %r--" % rc)
        

class ServerType(object):
    """ Represent a stock server. 
        
    """
    __metaclass__ = _serverTypeType
    # The server model object
    mcServer = None
    
    def __init__(self, mcServer):
        self.mcServer = mcServer
        self.log = logging.getLogger("server.allServerTypes.%s.%s" % (
                                                                      self.__class__.__name__,
                                                                      self.mcServer.name,
                                                                      ))
        self.log.debug("Creating a %r server (%r)" % (self.TYPE, self.__class__.__name__))
        
    def getServerRoot(self):
        return self.mcServer.loc()
    
    def getSessionName(self):
        return self.mcServer.getSessionName()
    
    # Tasks that should only be performed by the locally running Celery daemon
    def localInit(self):
        """ Perform first-round initialization tasks """
        import os, sys, os.path
        from shutil import copyfile
        
        try:
            os.mkdir(self.getServerRoot())
        except OSError:
            pass
        
        copyfile(
                 self.mcServer.bin.exc.path,
                 os.path.join(
                              self.getServerRoot(),
                              os.path.basename(self.mcServer.bin.exc.name),
                              ),
                 )
    
    def localLoadMap(self, mapSave):
        """ Load a saved map into the server. Overwrite if one already exists """
        # Remove old world
        import os, sys, os.path, shutil
        try:
            world = os.path.join(self.getServerRoot(), 'world')
            shutil.rmtree(world, ignore_errors = True)
        except:
            pass
        
        from zipfile import ZipFile
        from django.conf import settings
        zipLoc = os.path.join(settings.MC_MAP_SAVE_PATH, mapSave.zipName)
        zip = ZipFile(zipLoc, 'r')
        zip.extractall(self.getServerRoot())
        zip.close()
    
    def _localGenZipName(self, name, version):
        import datetime
        return "%05d_%s_%d-%d-%s_%s.zip" % (
                                      self.mcServer.pk,
                                      self.mcServer.bin.typeName,
                                      datetime.datetime.now().strftime('%Y-%m-%d_%H%M'),
                                      version
                                      )    

    def localSaveMap(self, name, desc = '', version = '', owner = None):
        """ Save the map in the map archive """
        from tempfile import mkstemp, mkdtemp
        from zipfile import ZipFile
        import os, sys, os.path, shutil
        
        zipName = self._localGenZipName(name, version)
        map = MapSave(name = name, desc = desc, version = version, owner = owner, zipName = zipName)
    
        mapPath = os.path.join(settings.MC_MAP_SAVE_PATH, zipName)
        orgMapPath = os.path.join(self.getServerRoot())
        
        assert os.access(orgMapPath, os.R_OK | os.W_OK)
        assert os.access(mapPath, os.R_OK)
        
        z, zpath = mkstemp()
        zip = ZipFile(z, 'w')
        zip.write(orgMapPath)
        zip.close()
        
        os.rename(z, mapPath)
        
        return map.pk
    
    def _simpleStartWait(self, args):
        """ Run the requested app. Collect all output and RC. """
        prg = subprocess.Popen(args, stderr = subprocess.PIPE, stdout = subprocess.PIPE)
        stdout, stderr = prg.communicate()        
        return dict(
                    rc = prg.returncode,
                    stdout = stdout,
                    stderr = stderr,
                    )
        
    def _logStartWait(self, args, cwd = None):
        """ Run the requested app. Log all output and RC. """
        # Run it
        prg = subprocess.Popen(args, stderr = subprocess.PIPE, stdout = subprocess.PIPE, cwd = cwd)
        # Log IO
        r = _IOLoggerThread(stream = prg.stdout, prg = prg, name = "%s.stdout" % args[0])
        r.start()
        r = _IOLoggerThread(stream = prg.stderr, prg = prg, name = "%s.stderr" % args[0])
        r.start()
        
        rc = prg.poll()
        while rc is None:
            self.log.debug("Still waiting for %r to complete" % args)
            rc = prg.poll()
        return rc
        
    
    def localStartServer(self):       
        """ Start a server
        @return: True=Start OK, False=Start Failed
        """
        jarPath = os.path.join(
                              self.getServerRoot(),
                              os.path.basename(self.mcServer.bin.exc.name),
                              )
        
        args = [
              "/usr/bin/screen",
              "-dmS",
              self.getSessionName(),
              '%s -Xmx%dM -Xms%dM %s %s >> %s/%s.log' % (
                                                        settings.MC_JAVA_LOC,
                                                        settings.MC_RAM_X,
                                                        settings.MC_RAM_S,
                                                        jarPath,
                                                        self.getSessionName(),
                                                        settings.MC_LOG_LOC,
                                                        self.getSessionName(),
                                                        ),
              ]
        
        rc = self._logStartWait(args, cwd = self.getServerRoot())
        if rc != 0:
            raise RuntimeError("Return code from screen non-zero: " + repr(rc))
        return rc == 0
    
    def localStopServer(self):
        rc = os.system("/usr/bin/screen -p 0 -S '%s' -X eval 'stuff \"say SERVER SHUTDOWN REQUESTED\"\015'" % (
                                                            self.getSessionName(),
                                                            ))
        if rc != 0:
            raise RuntimeError, "Return code from screen non-zero - say shutdown cmd: " + repr(rc)
        
        rc = os.system("/usr/bin/screen -p 0 -S '%s' -X eval 'stuff \"stop\"\015'" % (
                                                            self.getSessionName(),
                                                            ))
        if rc != 0:
            raise RuntimeError, "Return code from screen non-zero - stop cmd: " + repr(rc)
        
        return rc == 0
        
    def localSay(self, msg):
        rc = os.system("/usr/bin/screen -p 0 -S '%s' -X eval 'stuff \"say %s\"\015'" % (
                                                            self.getSessionName(),
                                                            msg,
                                                            ))
        if rc != 0:
            raise RuntimeError, "Return code from screen non-zero - say %r " % msg + repr(rc)
        
        return rc == 0
    
    def localStatus(self):
        rc = os.system("/usr/bin/screen -p 0 -S '%s' -X eval 'stuff \"list\"\015'" % (
                                                            self.getSessionName(),
                                                            ))
        
        return rc == 0
    
    # Override all var below this point
    
    # The 'name' (both human-readable and allServerTypes's key) for the server
    TYPE = None
    
    # Override all methods below this point

    
class StockServerType(ServerType):
    TYPE = "Stock"
    
    def __init__(self, *args, **kw):
        log.log(10, "Creating a %r server (%r)" % (self.TYPE, self.__class__.__name__))
        ServerType.__init__(self, *args, **kw)

class BannedIPSConfigFileType(ConfigFileType):
    # File match stuff
    FILE_MATCH = re.compile(r'^banned\-ips\.txt$')
    # Standard stuff
    SERVERTYPE = StockServerType.TYPE

class BannedPlayersConfigFileType(ConfigFileType):
    # File match stuff
    FILE_MATCH = re.compile(r'^players\-ips\.txt$')
    # Standard stuff
    SERVERTYPE = StockServerType.TYPE

class OpsConfigFileType(ConfigFileType):
    # File match stuff
    FILE_MATCH = re.compile(r'^ops\.txt$')
    # Standard stuff
    SERVERTYPE = StockServerType.TYPE

class ServerProperitiesConfigFileType(ConfigFileType):
    # File match stuff
    FILE_MATCH = re.compile(r'^server\.properties$')
    # Standard stuff
    SERVERTYPE = StockServerType.TYPE

class WhiteListConfigFileType(ConfigFileType):
    # File match stuff
    FILE_MATCH = re.compile(r'^white\-list\.txt$')
    # Standard stuff
    SERVERTYPE = StockServerType.TYPE

def getServerFromModel(mcServer):
    if allServerTypes.has_key(mcServer.bin.typeName):
        return allServerTypes[mcServer.bin.typeName]
    else:
        raise IndexError, "Server type %r not found" % mcServer.bin.typeName
 
def loadOtherServerTypes():
    """ Load server allServerTypes from other modules """
    # load the config
    from django.conf import settings    
    # Load any serverType modules
    for app in settings.INSTALLED_APPS:
        try:
            if app[:3] == 'mod':
                modName = "%s.serverType" % app
                stMod = __import__(modName)
                log.log(10, "Imported %r successfully", modName)
            else:
                log.log(10, "Skipping %r - Doesn't start with 'mod'", modName)
        except:
            log.log(15, "Importing %r failed", modName)
    log.log(10, "Tried to load all installed_apps")
