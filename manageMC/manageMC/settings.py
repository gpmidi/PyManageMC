''' PyManageMC specific defaults for Django and other related modules. 

settings.py = Defaults and recommended settings for PyManageMC
local_settings.py = Your settings

Created on Jul 21, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''

DEBUG = False
# DEBUG = True
TEMPLATE_DEBUG = DEBUG
DAJAXICE_DEBUG = DEBUG
DAJAXICE_NOTIFY_EXCEPTIONS = DEBUG
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
RAISE_EXCEPTIONS = DEBUG


# ADMINS = (
#     # ('Your Name', 'your_email@example.com'),
# )
#
# MANAGERS = ADMINS

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': '',  # Or path to database file if using sqlite3.
#         'USER': '',  # Not used with sqlite3.
#         'PASSWORD': '',  # Not used with sqlite3.
#         'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '',  # Set to empty string for default. Not used with sqlite3.
#     }
# }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'dajaxice.finders.DajaxiceFinder',
)

# Make this unique, and don't share it with anybody.
# SECRET_KEY = 'NO DEFAULTS FOR THIS'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'manageMC.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'manageMC.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOpenId',
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GoogleOAuth',
    'django_couchdb_utils.auth.backends.CouchDBAuthBackend',
)

SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
SOCIAL_AUTH_FORCE_EMAIL_VALIDATION = False

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # Make AJAX work easier
    'dajaxice',
    'dajax',
    # Celery - Distributed task queues
    'djcelery',
    # May be used later for JSON/XML RPC
    # 'rpc4django',
    # Used to help speed up file transfers by offloading the
    # reading and sending to the web server
    'sendfile',
    # External auth
    'social.apps.django_app.default',
    # CouchDB auth
    "django_couchdb_utils.auth",
    # A document-based NoSQL ORM
    'couchdbkit.ext.django',
    # Our stuff
    'extern',
    'minecraft',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTH_PROFILE_MODULE = 'extern.UserProfile'

TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.core.context_processors.tz",
        "django.contrib.messages.context_processors.messages",
        # "django.contrib.messages.context_processors.request",
        'social.apps.django_app.context_processors.backends',
        'social.apps.django_app.context_processors.login_redirect',
        "extern.requestPreProcessors.gaProcessor",
        "extern.requestPreProcessors.footerProcessor",
        "extern.requestPreProcessors.siteInfoProcessor",
    )

CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
# #        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#         'LOCATION': 'myhostname:11211',
#     }
}

SESSION_ENGINE = "django_couchdb_utils.sessions.couchdb"
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

##################################################################################
# PyManageMC
##################################################################################

# GA_ACCOUNT = "UA-nnnnnn-xx"

SITE_HUMAN_NAME = "My Minecraft Servers"
INTRO_TEXT = """ """

LEGAL_FOOTER = """ """

DAJAXICE_MEDIA_PREFIX = 'dajax'

MC_JAVA_LOC = "/usr/java/jre1.7.0_09/bin/java"
MC_RAM_X = 4096
MC_RAM_S = 1024
# MC_LOG_LOC = "/path/to/log/directory"
# MC_SERVER_PATH = "/path/to/servers/directory"
# MC_MAP_SAVE_PATH = "/path/to/maps/directory"


##################################################################################
# Celery
##################################################################################

# BROKER_URL = 'amqp://myusername:mypassword@myhostname:5672/myinstancename'
CELERY_RESULT_BACKEND = "amqp"
CELERYD_CONCURRENCY = 2
CELERYD_PREFETCH_MULTIPLIER = 2
BROKER_HEARTBEAT = True
BROKER_HEARTBEAT_CHECKRATE = 10
CELERY_REDIRECT_STDOUTS_LEVEL = "DEBUG"

# Don't keep any celery results longer than 1h to keep
# them from using up a lot of rabbitmq memory
from datetime import timedelta
TASK_RESULT_EXPIRES = timedelta(hours = 1)

import djcelery  # @UnresolvedImport
djcelery.setup_loader()
CELERY_DEFAULT_RATE_LIMIT = None
CELERY_DISABLE_RATE_LIMITS = True


##################################################################################
# RPC4Django
##################################################################################

# XML-RPC and JSON-RPC
RPC4DJANGO_LOG_REQUESTS_RESPONSES = False
RPC4DJANGO_RESTRICT_RPCTEST = True


##################################################################################
# Local Settings & Overrides
##################################################################################
from manageMC.local_settings import *



