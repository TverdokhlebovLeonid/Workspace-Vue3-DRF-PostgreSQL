from dotenv import load_dotenv

from config.env import env_bool, env_list, env_str
from config.settings.base import *

load_dotenv()
DEBUG = env_bool('DEBUG', default=True)
SECRET_KEY = env_str('SECRET_KEY', default='django-insecure-dev-only-change-me')
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'backend'])
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_str('POSTGRES_DB', default='workspace_app'),
        'USER': env_str('POSTGRES_USER', default='workspace_user'),
        'PASSWORD': env_str('POSTGRES_PASSWORD', default='workspace_password'),
        'HOST': env_str('POSTGRES_HOST', default='localhost'),
        'PORT': env_str('POSTGRES_PORT', default='5432'),
    }
}
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS', default=['http://localhost:5173', 'http://localhost:8080']
)
ENABLE_API_DOCS = env_bool('ENABLE_API_DOCS', default=True)
