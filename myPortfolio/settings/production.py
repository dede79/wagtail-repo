import os
import dj_database_url
from .base import *

DEBUG = False

ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')]

# Database — uses Render's PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
    )
}

# Security
SECRET_KEY = os.environ.get('SECRET_KEY')

# Whitenoise serves your static files (CSS/JS)
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware'] + MIDDLEWARE
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (uploaded images/docs)
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/render/project/src'