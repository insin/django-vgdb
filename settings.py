"""
Video game database settings.

A ``local_settings`` module must be made available to define sensitive
and highly installation-specific settings.

The following is a template for the settings which should be provided by
the ``local_settings`` module::

   # Database settings
   DATABASE_ENGINE = ''
   DATABASE_NAME = ''
   DATABASE_USER = ''
   DATABASE_PASSWORD = ''
   DATABASE_HOST = ''
   DATABASE_PORT = ''

   # URL that handles the media served from MEDIA_ROOT
   MEDIA_URL = ''

   # Make this unique and don't share it with anybody
   SECRET_KEY = ''

"""
import os

DIRNAME = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
USE_I8N = True

ADMINS = (
    ('Jonathan Buchanan', 'jonathan.buchanan@gmail.com'),
)

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

# Database settings will be obtained from a local_settings module

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/Belfast'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# Absolute path to the directory that holds media
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(DIRNAME, 'media')

# MEDIA_URL setting will be obtained from a local_settings module

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/"
ADMIN_MEDIA_PREFIX = '/media/'

# SECRET_KEY setting will be obtained from a local_settings module

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'vgdb.urls'

TEMPLATE_DIRS = (
    os.path.join(DIRNAME, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.databrowse',
    'mptt', # http://code.google.com/p/django-mptt/
    'vgdb',
)

try:
    from vgdb.local_settings import *
except ImportError:
    pass
