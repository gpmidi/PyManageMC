''' Django settings that override 'settings.py'
settings.py = Defaults and recommended settings for PyManageMC
local_settings.py = Your settings
'''
##################################################################################
# Django
##################################################################################

DEBUG = False
# DEBUG = True
TEMPLATE_DEBUG = DEBUG
DAJAXICE_DEBUG = DEBUG
DAJAXICE_NOTIFY_EXCEPTIONS = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# Keep this so MANAGERS gets any local_settings.py changes to ADMINS
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

# Our hostnames/domain-names/etc
ALLOWED_HOSTS = [
    ]

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/path/to/media'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/path/to/static/'

##### MAKE SURE TO CHANGE THIS! #####
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'CHANGE_ME'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/path/to/templates',
)

CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
# #        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#         'LOCATION': 'myhostname:11211',
#     }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

SITE_ID = 1

DEFAULT_FROM_EMAIL = 'nobody@example.com'


##################################################################################
# Celery
##################################################################################

BROKER_URL = 'amqp://myusername:mypassword@myhostname:5672/myinstancename'


##################################################################################
# PyManageMC
##################################################################################

SITE_HUMAN_NAME = "Test Server Minecraft"

MC_JAVA_LOC = "/path/to/bin/java"
MC_RAM_X = 1024
MC_RAM_S = 256
MC_LOG_LOC = "/path/to/logs"
MC_SERVER_PATH = "/path/to/srvs"
MC_MAP_SAVE_PATH = "/path/to/maps"

# GA_ACCOUNT = "UA-nnnnnn-xx"

INTRO_TEXT = """ """

LEGAL_FOOTER = """ """


##################################################################################
# CouchDB Stuff
##################################################################################
# App-to-DB mapping
COUCHDB_DATABASES = (
                     # ('projectname.appname','http://username:password@couchdbhostname:5984/vhostname'),
                     )


##################################################################################
# Large File Sending Via  Sendfile
##################################################################################
import os, os.path

SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = '/path/to/media/private'
SENDFILE_URL = '/media/private/'
