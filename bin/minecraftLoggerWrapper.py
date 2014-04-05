#!/usr/bin/python
"""

"""
# Logging
import logging
log = logging.getLogger('minecraftLoggerWrapper')

# Built-in
import os,os.path,sys
import threading

# External

# Ours


class WatchStream(threading.Thread):
    """ Log the IO for the given stream
    """
    
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
            if line != '' and line != '\n':
                self.log.log(self.level, "Read: " + line)            
            rc = self.prg.poll()
        line = self.stream.read()
        self.log.log(self.level, "Read: " + line)
        self.log.log(self.level, "-- Completed with a return code of %r --" % rc)
        




if __name__=="__main__":
    
    
    