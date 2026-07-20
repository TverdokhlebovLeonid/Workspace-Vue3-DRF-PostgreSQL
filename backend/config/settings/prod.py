from config.env import env_bool, env_list, env_str
from config.settings.base import *

DEBUG = False
SECRET_KEY = env_str('SECRET_KEY')
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_str('POSTGRES_DB'),
        'USER': env_str('POSTGRES_USER'),
        'PASSWORD': env_str('POSTGRES_PASSWORD'),
        'HOST': env_str('POSTGRES_HOST'),
        'PORT': env_str('POSTGRES_PORT', default='5432'),
    }
}
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', default=CORS_ALLOWED_ORIGINS)
ENABLE_API_DOCS = env_bool('ENABLE_API_DOCS', default=False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
JWT_AUTH_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
