from django.conf import settings
from django.http import HttpResponse

REFRESH_COOKIE_NAME = 'refresh_token'
REFRESH_COOKIE_PATH = '/api/auth/'


def _cookie_secure() -> bool:
    return getattr(settings, 'JWT_AUTH_COOKIE_SECURE', not settings.DEBUG)


def set_refresh_cookie(response: HttpResponse, refresh_token: str) -> None:
    max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=_cookie_secure(),
        samesite='Lax',
        path=REFRESH_COOKIE_PATH,
    )


def clear_refresh_cookie(response: HttpResponse) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value='',
        max_age=0,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        secure=_cookie_secure(),
        samesite='Lax',
    )
