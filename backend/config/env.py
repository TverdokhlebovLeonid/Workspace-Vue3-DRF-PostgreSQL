import os

from django.core.exceptions import ImproperlyConfigured


def env_bool(name: str, default: bool | None = None) -> bool:
    raw = os.getenv(name)
    if raw is None:
        if default is None:
            raise ImproperlyConfigured(f'Environment variable {name} is required.')
        return default
    return raw.lower() in ('1', 'true', 'yes', 'on')


def env_str(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == '':
        raise ImproperlyConfigured(f'Environment variable {name} is required.')
    return value


def env_list(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        if default is None:
            raise ImproperlyConfigured(f'Environment variable {name} is required.')
        return default
    return [item.strip() for item in raw.split(',') if item.strip()]
