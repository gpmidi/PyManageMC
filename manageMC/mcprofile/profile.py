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
Created on Aug 06, 2014

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
# Logging
import logging
log = logging.getLogger("mcprofile.profile")

# Built-in
import json
import hashlib
import urllib, urllib2

# External
import requests
from django.core.cache import get_cache

# Ours


class MinecraftUser(object):
    """
    """
    USER_SESSION_LOOKUP = 'https://sessionserver.mojang.com/session/minecraft/profile/'
    USERNAMES_TO_UUID = 'https://api.mojang.com/profiles/minecraft'
    USERNAMES_TO_UUID_HEADERS = {"Content-Type": "application/json"}
    SESSION_CACHE_TIME_SECONDS = 60

    def __init__(self, uuid=None, username=None):
        assert uuid or username, "Expected either uuid or username to be defined"
        self.cache = get_cache('default')
        self._uuid = uuid
        self._session = None
        if username:
            self._uuid = self.usernameToUUID(username)
        self._username = username

    @property
    def uuid(self):
        assert self._uuid, "Expected a valid UUID for %r" % self
        return self._uuid

    @property
    def username(self):
        if not self._username:
            self._username = self.session['name']
        return self._username

    @property
    def session(self):
        if not self._session:
            self._session = self.getSession(self.uuid)
        return self._session

    def getSession(self, uuid):
        k = self.makeKey("uuid->session", uuid)
        ses = self.cache.get(k)
        if ses:
            return ses
        ses = self.uuidToSession(uuid)
        self.cache.set(k, ses, self.SESSION_CACHE_TIME_SECONDS)
        if ses is None:
            raise ValueError("Couldn't find a session/profile for %r" % uuid)
        return ses

    @classmethod
    def uuidToSession(cls, uuid):
        req = requests.get(cls.USER_SESSION_LOOKUP + urllib.quote(uuid))
        if req.text == '':
            return None
        return req.json()

    @classmethod
    def makeKey(cls, typ, *data):
        h = hashlib.new('SHA1')
        h.update(cls.__class__.__name__)
        h.update(typ)
        for i in data:
            h.update(str(i))
        return h.hexdigest()

    def usernameToUUID(self, username):
        k = self.makeKey("username->uuid", username)
        uuid = self.cache.get(k)
        if uuid:
            return uuid
        for name, uuid in self.usernamesToUUID([username, ]).items():
            if name == username:
                self.cache.set(k, uuid, None)
                return uuid
        raise ValueError("Username %r wasn't found" % username)

    @classmethod
    def usernamesToUUID(cls, usernames):
        req = requests.post(
                            cls.USERNAMES_TO_UUID,
                            headers=cls.USERNAMES_TO_UUID_HEADERS,
                            data=json.JSONEncoder().encode(usernames),
                            )

        ret = {}
        for info in req.json():
            ret[info['name']] = info['id']

        return ret
