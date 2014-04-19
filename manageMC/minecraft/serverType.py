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

# Built-in
import re  # @UnusedImport
import os, os.path, sys, shutil  # @UnusedImport
import time
import hashlib
import difflib
import xmlrpclib
from contextlib import contextmanager
import zipfile  # @UnusedImport
from StringIO import StringIO  # @UnusedImport
import tempfile
import subprocess
import datetime

# External
from django.template.loader import render_to_string
from supervisor import supervisord, supervisorctl  # @UnresolvedImport @UnusedImport

# Ours
from minecraft.models import *  # @UnusedWildImport

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

    # The template to use when the file doesn't already exist
    TEMPLATE_INIT = None

    def __init__(self, serverDir, minecraftServerObj):
        self.serverDir = serverDir
        self.minecraftServerObj = minecraftServerObj

    def getModelClassID(self):
        return self.getModelClass(
            ).makeServerID(
               minecraftServerPK=self.minecraftServerObj.pk,
               )

    def getMyModel(self):
        cls = self.getModelClass()
        obj = cls.get_or_create(self.getModelClassID())
        return (cls, obj)

    def matchFile(self, filePath):
        """ filePath should be relative to the base of the server
        directory.
        """
        assert filePath[0] != '/'
        return self.FILE_MATCH.match(filePath)

    def getAllConfigs(self):
        """ Return a list of all config files that are of our type """
        for (dirpath, dirnames, filenames) in os.walk(self.serverDir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                filerel = os.path.relpath(filepath, self.serverDir)
                if self.matchFile(filerel):
                    yield dict(filepath=filepath, relativepath=filerel)

    def parseConfig(self, filepath, relativepath, filedata):
        """ Parse the given config file and return a dict of strings
        that should be saved to the DB.
        @note: This call may not always be used; The saveConfig method may be overridden in a way that doesn't use this method.
        """
        return dict(filepath=filepath, relativepath=relativepath, filedata=filedata)

    def saveConfig(self, filepath, relativepath, filedata):
        """ Parse the given config file and then save the results to
        the DB """
        parsed = self.parseConfig(filepath, relativepath, filedata)
        cls = self.getModelClass()
        obj = cls.get_or_create(self.getModelClassID())

        for k, v in parsed.items():
            setattr(obj, k, v)

        obj.save()
        return self.getModelClassID()

    def renderConfig(self, relativepath):
        assert self.TEMPLATE_INIT, "%r needs a valid TEMPLATE_INIT" % self

        cls = self.getModelClass()
        obj = cls.get_or_create(self.getModelClassID())

        return render_to_string(
                              self.TEMPLATE_INIT,
                              dict(
                                   fileType=self,
                                   fileRelPath=relativepath,
                                   fileData=obj,
                                   server=self.minecraftServerObj,
                                   ),
                              )

    def writeConfig(self, filepath, relativepath):
        """ Write this config file data to the given file """
        with open(filepath, 'wb') as f:
            f.write(self.renderConfig(relativepath=relativepath))


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

    def __init__(self, stream, prg, name='Unnamed', loglevel=20):
        threading.Thread.__init__(self)
        self.level = loglevel
        self.stream = stream
        self.prg = prg
        self.streamname = name
        self.setName(name="IOReaderThread-%s" % name)
        self.log = logging.getLogger("server.allServerTypes." + name)
        self.log.debug("Creating IO logger %r (%r)" % (name, self.getName()))
        self.setDaemon(True)

    def run(self):
        rc = self.prg.poll()
        while rc is None:
            line = self.stream.readline()
            if line != '' and line != '\n':
                self.log.log(self.level, "Read: " + line)
            rc = self.prg.poll()
        line = self.stream.read()
        self.log.log(self.level, "Read: " + line)
        self.log.log(self.level, "-- Completed with a return code of %r --" % rc)


class ServerType(object):
    """ Represent a stock server.

    """
    __metaclass__ = _serverTypeType
    # The server model object
    mcServer = None

    class ConfigUpdateResult(object):
        def __init__(self, oldHashDB, oldHashFS, oldFileDB, oldFileFS, hashType='SHA512'):
            self.oldHashDB = oldHashDB
            self.oldHashFS = oldHashFS
            self.oldFileDB = oldFileDB
            self.oldFileFS = oldFileFS
            self.hashType = hashType


    class SuccessConfigUpdateResult(ConfigUpdateResult):
        def __init__(self, newHashDB, newFileDB, newHashFS, newFileFS, **kw):
            ServerType.ConfigUpdateResult.__init__(self, **kw)
            self.newHashDB = newHashDB
            self.newFileDB = newFileDB
            self.newHashFS = newHashFS
            self.newFileFS = newFileFS


    class FailConfigUpdateResult(ConfigUpdateResult):
        def __init__(self, newHashDB, newFileDB, fileDiff, **kw):
            ServerType.ConfigUpdateResult.__init__(self, **kw)
            self.newHashDB = newHashDB
            self.newFileDB = newFileDB
            self.fileDiff = fileDiff


    class ExistsFailConfigUpdateResult(ConfigUpdateResult):
        def __init__(self, newHashDB, newFileDB, **kw):
            ServerType.ConfigUpdateResult.__init__(self, **kw)
            self.newHashDB = newHashDB
            self.newFileDB = newFileDB


    def __init__(self, mcServer):
        self.mcServer = mcServer
        self.log = logging.getLogger("server.allServerTypes.%s.%s" % (
                                                                      self.__class__.__name__,
                                                                      self.mcServer.name,
                                                                      ))
        self.log.debug("Creating a %r server (%r)" % (self.TYPE, self.__class__.__name__))

        assert self.mcServer.type == self.TYPE
        self._supervisorProxy = None

    def _makeCacheID(self, fname, *varyOn, **kwargs):
        h = hashlib.new('sha512')
        h.update(str(fname))
        if kwargs.get('varyOnSelf', True):
            h.update(str(self.mcServer._id))
        for i in varyOn:
            h.update(str(i))
        h.update(str(settings.SECRET_KEY))
        return h.hexdigest()

    @property
    def containerInfo(self):
        from mcdocker.tasks import inspectDockerContainer
        return inspectDockerContainer.delay(
                containerID=self.mcServer.container).get()

    def getPortMappings(self):
        """ Return raw port bindings for this instance
        @note: This is slow as it requires an async XML-RPC request
        Return schema:
            "8888/tcp": [
                {
                    "HostIp": "0.0.0.0",
                    "HostPort": "9999"
                }
            ]
        """
        return self.containerInfo["HostConfig"]["PortBindings"]

    def getPortMapping(self, port, protocol='tcp', forceRefresh=False):
        """
        @return: List of (addy,port) tuples
        """
        assert protocol in ['tcp', 'udp'], "Expected 'tcp' or 'udp'"
        internalName = "%d/%s" % (port, protocol)

        cacheKey = self._makeCacheID('getPortMapping', internalName)

        if forceRefresh:
            mappings = self.getPortMappings()
            if internalName in mappings:
                ret = []
                for mp in mappings[internalName]:
                    if 'HostIp' in mp and 'HostPort' in mp:
                        ret.append((mp['HostIp'], mp['HostPort']))
                    elif 'HostPort' in mp:
                        ret.append(('127.0.0.1', mp['HostPort']))
            else:
                ret = None
            caches['default'].set(cacheKey, json.dumps(ret), 60)
            return ret
        else:
            try:
                return json.loads(caches['default'].get(cacheKey))
            except:
                return self.getPortMapping(
                                           port=port,
                                           protocol=protocol,
                                           forceRefresh=True,
                                           )

    @property
    def supervisordHostPort(self):
        return self.getPortMapping(
                                   port=settings.MINECRAFT_DEFAULT_PORT_SUPVD,
                                   protocol='tcp',
                                   )

    @property
    def sshdHostPort(self):
        return self.getPortMapping(
                                   port=settings.MINECRAFT_DEFAULT_PORT_SSH,
                                   protocol='tcp',
                                   )

    @property
    def minecraftHostPort(self):
        return self.getPortMapping(
                                   port=settings.MINECRAFT_DEFAULT_PORT_CONTAINER,
                                   protocol='tcp',
                                   )

    @property
    def rconHostPort(self):
        return self.getPortMapping(
                                   port=settings.MINECRAFT_DEFAULT_PORT_RCON,
                                   protocol='tcp',
                                   )

    @property
    def instance(self):
        """ Returns the minecraft server object for hosted instances
        or None if it is not hosted """
        return self.mcServer.getInstance()

    @property
    def image(self):
        return self.mcServer.getImage()

    @property
    def supervisordConnInfo(self):
        """ URL to the XML-RPC interface for our Docker instance's supervisor
        """
        # TODO: Catch errors around this if no ports are bound
        cacheKey = self._makeCacheID('supervisordConnInfo')
        try:
            ret = json.loads(caches['default'].get(cacheKey))
        except:
            import urllib
            ret = "http://%s:%s@%s:%s/RPC2" % (
                      urllib.quote(self.getImage.supervisordUser),
                      urllib.quote(self.getImage.realSupervisordPasswd),
                      urllib.quote(self.supervisordHostPort[0][0]),
                      urllib.quote(self.supervisordHostPort[0][1]),
                      )
            caches['default'].set(cacheKey, json.dumps(ret), 60)
        return ret

    @property
    def supervisordProxy(self):
        """ Returns an XML-RPC Server Proxy to Supervisord in our Docker
        instance """
        if self._supervisorProxy is None:
            self._supervisorProxy = xmlrpclib.ServerProxy()
        try:
            self._supervisorProxy.system.listMethods()
        except Exception as e:
            self.log.exception("Failed to run listMethods on %r in %r with %r", self._supervisorProxy, self, e)
            self._supervisorProxy = xmlrpclib.ServerProxy()
        return self._supervisorProxy

    @property
    def serverRoot(self):
        """ Path to the minecraft instance directory from inside docker """
        return self.mcServer.getVolumeLocation('minecraft')

    @property
    def volumes(self):
        """ Return dict of volumes in <real path>:<docker path>"""
        return self.containerInfo["Volumes"]

    @property
    def realServerRoot(self):
        """ Path to the minecraft instance directory from inside docker """
        return self.volumes[self.serverRoot]

    @property
    def sessionName(self):
        return self.mcServer.getSessionName()

    @property
    def pk(self):
        return self.mcServer._id

    @property
    def supervisordState(self):
        # http://supervisord.org/api.html?highlight=python#supervisor.rpcinterface.SupervisorNamespaceRPCInterface.getState
        return self.supervisordProxy.supervisor.getState()['statename']

    @property
    def isRunning(self):
        """ Make sure the docker instance, supervisord, and minecraft instance
        are running
        """
        # TODO: Look into adding a RESTARTING check
        return  self.supervisordState == "RUNNING" \
            and self.minecraftProcState == "RUNNING"

    @property
    def minecraftProcInfo(self):
        # http://supervisord.org/api.html?highlight=python#supervisor.rpcinterface.SupervisorNamespaceRPCInterface.getProcessInfo
        return self.supervisordProxy.supervisor.getProcessInfo('minecraft')

    @property
    def supervisordIsRunning(self):
        # http://supervisord.org/api.html?highlight=python#supervisor.rpcinterface.SupervisorNamespaceRPCInterface.getProcessInfo
        return self.supervisordState['statename'] == "RUNNING"

    def runCommand(self, cmd):
        """ Run a command on the given server """
        self.log.debug("Going to run %r on %r", cmd, self)

        if not self.isRunning:
            raise RuntimeError("Expected supervisord to be running for %r" % self)

        self.supervisordProxy.supervisor.sendProcessStdin(
                  'minecraft',
                  cmd + "\n",
                  )

    def sendStopCommand(self):
        """ Send the stop command to the server """
        # TODO: Add a wait option
        self.runCommand('stop')

    def sendSay(self, message):
        """ Send a message to all as the server """
        # FIXME: Add validation
        self.runCommand('say %s' % message)

    def sendSaveOn(self):
        self.runCommand('save-on')

    def sendSaveOff(self):
        self.runCommand('save-off')

    def sendSaveAll(self):
        self.runCommand('save-all')

    @contextmanager
    def ctxMgrSaveOff(self):
        """ A context manager that will temp disable map saving while
        it's running
        """
        self.sendSaveAll()
        self.sendSaveOff()
        self.sendSaveAll()
        yield
        self.sendSaveAll()
        self.sendSaveOn()
        self.sendSaveAll()

    def _localGenZipName(self, name, version):
        return "%09s_%s_%s_%s.zip" % (
                                      self.pk,
                                      self.mcServer.bin.typeName,
                                      datetime.datetime.now().strftime('%Y-%m-%d_%H%M'),
                                      version
                                      )

    def saveMap(self, msId):
        ms = MapSave.get(msId)
        name = self._localGenZipName(ms.name, ms.version)
        tdir = tempfile.mkdtemp(prefix=str(self.pk))
        zf = os.path.join(tdir, name)

        try:
            with self.ctxMgrSaveOff():
                args = [
                        '/usr/bin/zip',
                        '--suffixes',  # Pointless since we don't compress
                        '.mca',
                        '--quiet',
                        '--recurse-paths',
                        '--archive-comment',
                        'Minecraft Map For %s on %s' % (
                                    self.pk,
                                    datetime.datetime.utcnow().isoformat(),
                                    ),
                        '--no-extra',
                        '--compression-method',
                        'store',
                        zf,
                        ] + self.getMapFilenames()
                p = subprocess.Popen(args, cwd=self.serverRoot)
                rc = p.wait()
                if rc != 0:
                    raise RuntimeError("Failed to save map. Zip returned %d" % rc)

            with open(zf, 'rb') as f:
                ms.put_attachment(f, name=name)
            ms.save()

        finally:
            try:
                shutil.rmtree(tdir, True)
            except:
                pass

    def loadMap(self, msId):
        """ Load a saved map into the server. Overwrite if one already exists """

        if self.isRunning:
            raise RuntimeError("Server %r can't be running during a map load" % self)

        ms = MapSave.get(msId)

        # Remove old world
        worlds = self.getMapFilenames()
        for world in worlds:
            try:
                shutil.rmtree(world, ignore_errors=True)
            except Exception, e:
                self.log.exception("Failed to remove %r with %r", world, e)

        # Extract the world
        with tempfile.NamedTemporaryFile(
                                         mode='wb',
                                         prefix=str(self.pk),
                                         suffix='.zip',
                                         ) as f:
            for block in ms.fetch_attachment(name=ms.name, stream=True):
                f.write(block)
            # Must be done inside the namedtemp with
            args = [
                    '/usr/bin/unzip',
                    '-d',
                    self.serverRoot,
                    '-o',  # overwrite without warning
                    '-q',  # quiet
                    f.name,
                    ] + self.getMapFilenames()
            p = subprocess.Popen(args, cwd=self.serverRoot)
            rc = p.wait()
            if rc != 0:
                raise RuntimeError("Failed to save map. Zip returned %d" % rc)


    def getMapFilenames(self):
        # TODO: Support world names beyond 'world'
        return [
                os.path.join(self.serverRoot, 'world'),
                # Not needed for vanilla
                # os.path.join(self.serverRoot, 'world_nether'),
                # os.path.join(self.serverRoot, 'world_the_end'),
                ]


    def init(self):
        """ Perform first-round initialization tasks """
        from shutil import copyfile

        for path in [
                     # Needs to be before most others as they are subdirectories
                     self.serverRoot,
                     ]:
            try:
                os.makedirs(path, 0770)
            except OSError:
                pass

        copyfile(
                 self.mcServer.bin.exc.path,
                 os.path.join(
                              self.serverRoot,
                              os.path.basename(self.mcServer.bin.exc.name),
                              ),
                 )

    def startServer(self, wait=True):
        """ Start a server
        @return: True=Start OK, False=Start Failed
        """
        self.log.info("Going to start %r", self)
        return self.supervisordProxy.supervisor.startProcess('minecraft', wait)

    def killServer(self, wait=True):
        """ Kill a server
        @return: True=Kill OK, False=Kill Failed
        """
        self.log.info("Going to stop %r", self)
        return self.supervisordProxy.supervisor.stopProcess('minecraft', wait)

    def stopServer(self, killAfter=60, wait=True, warn=True, warnDelaySeconds=0):
        self.log.info("Going to stop %r", self)
        if warn:
            # Tell the users we are shutting down
            self.localSay(msg="SERVER SHUTDOWN SOON")
            if warnDelaySeconds and warnDelaySeconds > 0:
                time.sleep(warnDelaySeconds)
        # Gracefully stop the server
        self.sendStopCommand()

        start = time.time()
        if killAfter is not None:
            while self.isRunning:
                time.sleep(1)
                if start + killAfter > time.time():
                    return self.killServer(wait=wait)

        # Success
        return True

    def localRunCommand(self, cmd):
        """ Run a server command. """

#
#
#         self.log.debug("Going to run %r on %r", cmd, self)
#         # Tell the users we are shutting down
#         args = [
#               "/usr/bin/screen",
#               "-p",
#               "0",
#               "-S",
#               self.getSessionName(),
#               "-X",
#               "eval",
#               # FIXME: Validate escaping is working right here
#               "stuff %r\015" % cmd,
#               ]
#         self._logStartWaitError(args=args, cwd=self.serverRoot)
        return True

    def localSay(self, msg):
        self.log.info("Going to say %r on %r", msg, self)
        self.localRunCommand(cmd="say %s" % str(msg))
        return True

    def localStatus(self):
        self.log.info("Going to run 'list' on %r", self)
        self.localRunCommand(cmd="list")
        return True

    def localForceSave(self):
        self.log.info("Going to run 'save-all' on %r", self)
        self.localRunCommand(cmd="save-all")
        return True

    def localEnableAutoSave(self):
        self.log.info("Going to run 'save-on' on %r", self)
        self.localRunCommand(cmd="save-on")
        return True

    def localDisableAutoSave(self):
        self.log.info("Going to run 'save-off' on %r", self)
        self.localRunCommand(cmd="save-off")
        return True

    def localGetConfigFile(self, filename):
        """ Return the current contents of the given file. The
        filename should be relitiave to the server root.
        """
        with open(os.path.join(self.serverRoot, filename), 'r') as f:
            return f.read()

    def localUpdateDBConfigFile(self, fileTypeObj):
        """ Update couchdb with the current contents of the
        requested config file.
        """
        assert isinstance(fileTypeObj, FileType), "Expected %r to be FileType based" % fileTypeObj

        confTxt = self.localGetConfigFile(filename=fileTypeObj.FILE_NAME)

        pk = fileTypeObj.saveConfig(
                               filepath=os.path.join(self.serverRoot, fileTypeObj.FILE_NAME),
                               relativepath=fileTypeObj.FILE_NAME,
                               filedata=confTxt,
                               )
    @staticmethod
    def _hashFile(filePath):
        with open(filePath, 'rb') as f:
            data = f.read()
            h = hashlib.new('sha512', data)
        return (h.hexdigest().lower(), data)

    def localUpdateConfigFile(self, fileTypeObj, errorOnFail=True):
        """ Update the config file with data from couchdb.
        """
        assert isinstance(fileTypeObj, FileType), "Expected %r to be FileType based" % fileTypeObj

        filePath = os.path.join(self.serverRoot, fileTypeObj.FILE_NAME)
        relPath = fileTypeObj.FILE_NAME
        (cls, dbObj) = fileTypeObj.getMyModel()

        results = dict(
                       oldHashDB=dbObj.nc_lastHash,
                       oldHashFS=None,
                       oldFileDB=dbObj.getConfigFile(),
                       oldFileFS=None,
                       # hashType='SHA512',
                       )

        if os.path.exists(filePath):
            results['oldHashFS'], results['oldFileFS'] = self._hashFile(filePath)

        newCfg = fileTypeObj.renderConfig(relativepath=relPath)
        h = hashlib.new('sha512', newCfg)
        results['newHashDB'] = h.hexdigest().lower()
        results['newFileDB'] = newCfg

        # Make sure the file matches what we were told to expect
        if  results['oldHashDB'] is None:
            log.debug("I've been told %r won't exist", fileTypeObj)
            if os.path.exists(filePath):
                log.info("File %r exists but I was told it wouldn't exist", filePath)
                if errorOnFail:
                    raise IOError("File %r exists but I was told it wouldn't exist" % filePath)
                else:
                    return ServerType.ExistsFailConfigUpdateResult(**results)
            else:
                log.debug("Config file %r doesn't exist as was expected. ", filePath)
        else:
            log.debug("I've been told %r will exist and that it's sha512 is %r", fileTypeObj, results['oldHashDB'])
            if results['oldHashFS'] == results['oldHashDB']:
                log.debug("SHA512 checksums match %r=%r", results['oldHashFS'], results['oldHashDB'])
            else:
                log.info("SHA512 checksums for %r don't match: %r!=%r", filePath, results['oldHashFS'], results['oldHashDB'])
                if errorOnFail:
                    raise ValueError("SHA512 checksums for %r don't match: %r!=%r", filePath, results['oldHashFS'], results['oldHashDB'])
                else:
                    if results['oldFileDB'] and results['oldFileFS']:
                        results['fileDiff'] = '\n'.join(difflib.unified_diff(
                             results['oldFileDB'].splitlines(),
                             results['oldFileFS'].splitlines(),
                             fromfile='oldFileDB',
                             tofile='oldFileFS',
                             ))
                    else:
                        results['fileDiff'] = None
                    return ServerType.FailConfigUpdateResult(**results)

        fileTypeObj.writeConfig(
                                filepath=filePath,
                                relativepath=relPath,
                                )

        results['newHashFS'], results['newFileFS'] = self._hashFile(filePath)
        results['oldHashFS'] = results['newHashFS']
        results['oldHashDB'] = results['newFileFS']
        return ServerType.SuccessConfigUpdateResult(**results)


#     def _simpleStartWait(self, args):
#         """ Run the requested app. Collect all output and RC. """
#         prg = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
#         stdout, stderr = prg.communicate()
#         return dict(
#                     rc=prg.returncode,
#                     stdout=stdout,
#                     stderr=stderr,
#                     )
#
#     def _logStartWait(self, args, cwd=None):
#         """ Run the requested app. Log all output and RC. """
#         self.log.debug("Running %r in %r", args, cwd)
#         # Run it
#         prg = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)
#         # Log IO
#         r = _IOLoggerThread(stream=prg.stdout, prg=prg, name="%s.stdout" % args[0])
#         r.start()
#         r = _IOLoggerThread(stream=prg.stderr, prg=prg, name="%s.stderr" % args[0])
#         r.start()
#
#         rc = prg.poll()
#         while rc is None:
#             self.log.debug("Still waiting for %r to complete" % args)
#             rc = prg.poll()
#         self.log.debug("RC from %r is %r", args, rc)
#         return rc
#
#     def _logStartWaitError(self, args, cwd=None):
#         """ Run the requested app. Log all output and RC. Generate an error if RC!=0. """
#         rc = self._logStartWait(args=args, cwd=cwd)
#         if rc != 0:
#             self.log.debug("Command %r failed with an RC of %r", args, rc)
#             raise RuntimeError("Return code from %r non-zero: %r" % (args, rc))
#         return rc

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
    FILE_MATCH = re.compile(r'^banned\-players\.txt$')
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
    # Our config file name relitive to the server root
    FILE_NAME = 'server.properties'
    # Used to create the file
    TEMPLATE_INIT = 'configs/server.properties'

    def getModelClass(self):
        from minecraft.models import MinecraftServerProperties
        return MinecraftServerProperties

    def parseConfig(self, filepath, relativepath, filedata):
        """ Parse the given config file and return a dict of strings
        that should be saved to the DB.
        @note: This call may not always be used; The saveConfig method may be overridden in a way that doesn't use this method.
        """
        ret = self.rawParseConfig(filedata)
        for k, v in ret.items():
            found = filter(
                           lambda x: x[1].name == k,
                           self.getModelClass().properties().items(),
                           )
            assert len(found) <= 1, "Found more than one property with the right name: %r / %r / %r" % (found, k, v)
            if len(found) == 1:
                found = map(lambda x: dict(
                                           propName=x[1].name,
                                           attrName=x[0],
                                           obj=x[1],
                                           dataType=x[1].data_type,
                                           ), found)[0]
                ret[k] = self.convertType(
                                           strValue=v,
                                           **found
                                           )
            else:
                pass

        ret['nc_configFileTypeName'] = str(relativepath)
        ret['nc_minecraftServerPK'] = self.minecraftServerObj.pk
        return ret

    CT_NONE_VALUES = [
                    'null',
                    'none',
                    ]
    CT_TRUE_VALUES = [
                    'true',
                    '1',
                    'y',
                    ]
    CT_FALSE_VALUES = [
                    'false',
                    '0',
                    'n',
                    ]
    def convertType(self, propName, attrName, strValue, obj, dataType):
        assert isinstance(strValue, str)
        strValue = strValue.lower()

        # Handle Nulls
        if len(strValue) == 0:
            return None
        if strValue in self.CT_NONE_VALUES:
            return None

        if dataType is bool:
            if strValue in self.CT_TRUE_VALUES:
                return True
            elif strValue in self.CT_FALSE_VALUES:
                return False
            raise ValueError("%r is not %r.%r" % (strValue, dataType, obj))
        if dataType is str:
            return str(strValue)
        if dataType is unicode:
            return unicode(strValue)
        if dataType is int:
            return int(strValue)

        raise ValueError("%r is not %r.%r" % (strValue, dataType, obj))


    RE_PARSE_CONFIG = re.compile(r'^\s*([a-zA-Z0-9\-]+)\s*=(?:\s*?(.*)\s*?)?$', re.MULTILINE)
    @classmethod
    def rawParseConfig(cls, fileContents):
        ret = {}
        for k, v in cls.RE_PARSE_CONFIG.findall(fileContents):
            ret[k] = v
        return ret

    def writeConfig(self, filepath, relativepath):
        """ Write this config file data to the given file """
        assert self.TEMPLATE_INIT, "%r needs a valid TEMPLATE_INIT" % self

        cls = self.getModelClass()
        obj = cls.get_or_create(self.getModelClassID())
        fileData = {}

        # TODO: May need to fix this.
        for k, v in obj.items():
            fileData[str(k)] = str(v)

        data = render_to_string(
                              self.TEMPLATE_INIT,
                              dict(
                                   fileType=self,
                                   fileRelPath=relativepath,
                                   fileData=fileData,
                                   server=self.minecraftServerObj,
                                   ),
                              )
        with open(filepath, 'w') as f:
            f.write(data)


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
