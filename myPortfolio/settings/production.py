import os
import dj_database_url
from .base import *

DEBUG = False

ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')]

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

SECRET_KEY = os.environ.get('SECRET_KEY')

MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware'] + MIDDLEWARE
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = 'https://res.cloudinary.com/dn5nn8omf/'

WAGTAILIMAGES_IMAGE_MODEL = 'wagtailimages.Image'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'