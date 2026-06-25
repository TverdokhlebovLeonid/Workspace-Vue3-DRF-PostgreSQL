from config.settings.base import *

SECRET_KEY = 'test-secret-key-not-for-production'
DEBUG = False
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
CORS_ALLOWED_ORIGINS = []
ENABLE_API_DOCS = False
