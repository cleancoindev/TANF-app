"""Define settings for all environments."""

import logging
import os
from distutils.util import strtobool
from os.path import join
from secrets import token_urlsafe

from configurations import Configuration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# NOTE: These may be overridden by system or env_file variables
#       Eventually we may want to consider moving these defaults into
#       settings declarations in the class below. This will allow us to safely
#       reference environment variables across the app as we will no longer
#       need to rely on calling os.environ directly.
os.environ.setdefault("BASE_URL", "http://localhost:8080/v1")
os.environ.setdefault("FRONTEND_BASE_URL", "http://localhost:3000")


class Common(Configuration):
    """Define configuration class."""

    INSTALLED_APPS = (
        "colorfield",
        "admin_interface",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third party apps
        "rest_framework",  # Utilities for rest apis
        "rest_framework.authtoken",  # Token authentication
        "django_filters",
        "django_admin_logs",  # logs for admin site
        "corsheaders",
        "django_extensions",
        "drf_yasg",
        "storages",
        # Local apps
        "tdpservice.core.apps.CoreConfig",
        "tdpservice.users",
        "tdpservice.stts",
        "tdpservice.reports",
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "tdpservice.users.api.middleware.AuthUpdateMiddleware",
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = "tdpservice.urls"
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", token_urlsafe(50))
    WSGI_APPLICATION = "tdpservice.wsgi.application"
    CORS_ORIGIN_ALLOW_ALL = True

    # Email Server
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    # Whether to use localstack in place of a live AWS S3 environment
    USE_LOCALSTACK = bool(strtobool(os.getenv("USE_LOCALSTACK", "no")))

    # Those who will receive error notifications from django via email
    ADMINS = (("Admin1", "ADMIN_EMAIL_FIRST"), ("Admin2", "ADMIN_EMAIL_SECOND"))

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
        }
    }

    # General
    APPEND_SLASH = True
    TIME_ZONE = "UTC"
    LANGUAGE_CODE = "en-us"
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_URL = "/v1/login/oidc"
    LOGIN_REDIRECT_URL = "/"

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    STATICFILES_DIRS = []
    STATIC_URL = "/static/"
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )

    # By default collectstatic will store files locally so these settings are
    # not used but they must be defined, lest the server will fail to startup.
    AWS_S3_STATICFILES_ACCESS_KEY = None
    AWS_S3_STATICFILES_SECRET_KEY = None
    AWS_S3_STATICFILES_BUCKET_NAME = None
    AWS_S3_STATICFILES_ENDPOINT = None
    AWS_S3_STATICFILES_REGION_NAME = None

    # Store uploaded files in S3
    # http://django-storages.readthedocs.org/en/latest/index.html
    DEFAULT_FILE_STORAGE = 'tdpservice.backends.DataFilesS3Storage'
    AWS_S3_DATAFILES_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_S3_DATAFILES_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_DATAFILES_BUCKET_NAME = os.getenv('AWS_BUCKET')
    AWS_S3_DATAFILES_REGION_NAME = os.getenv('AWS_REGION_NAME', 'us-gov-west-1')
    AWS_S3_DATAFILES_ENDPOINT = \
        f'https://s3-{AWS_S3_DATAFILES_REGION_NAME}.amazonaws.com'

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), "media")
    MEDIA_URL = "/media/"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": STATICFILES_DIRS,
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "no"))

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": (
                "django.contrib.auth.password_validation."
                "UserAttributeSimilarityValidator"
            ),
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[%(server_time)s] %(message)s",
            },
            "verbose": {
                "format": (
                    "%(levelname)s %(asctime)s %(module)s "
                    "%(process)d %(thread)d %(message)s"
                )
            },
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
        "handlers": {
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        "loggers": {
            "django": {"handlers": ["console"], "propagate": True},
            "django.server": {
                "handlers": ["django.server"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["mail_admins", "console"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.db.backends": {"handlers": ["console"], "level": "INFO"},
        },
    }

    # Custom user app
    AUTH_USER_MODEL = "users.User"

    # Sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_TIMEOUT = 30

    # The CSRF token Cookie holds no security benefits when confined to HttpOnly.
    # Setting this to false to allow the frontend to include it in the header
    # of API POST calls to prevent false negative authorization errors.
    # https://docs.djangoproject.com/en/2.2/ref/settings/#csrf-cookie-httponly
    CSRF_COOKIE_HTTPONLY = False
    CSRF_TRUSTED_ORIGINS = ['.app.cloud.gov', '.acf.hhs.gov']

    SESSION_COOKIE_PATH = "/;HttpOnly"

    # Django Rest Framework
    REST_FRAMEWORK = {
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": int(os.getenv("DJANGO_PAGINATION_LIMIT", 10)),
        "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
        "DEFAULT_RENDERER_CLASSES": (
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ),
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "tdpservice.users.authentication.CustomAuthentication",
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ),
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend",
        ],
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
        "TEST_REQUEST_RENDERER_CLASSES": [
            "rest_framework.renderers.MultiPartRenderer",
            "rest_framework.renderers.JSONRenderer"
        ],
    }

    AUTHENTICATION_BACKENDS = (
        "tdpservice.users.authentication.CustomAuthentication",
        "django.contrib.auth.backends.ModelBackend",
    )

    # CORS
    CORS_ALLOW_CREDENTIALS = True

    # Capture all logging statements across the service in the root handler
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())

    ###
    # AV Scanning Settings
    #

    # The URL endpoint to send AV scan requests to (clamav-rest)
    AV_SCAN_URL = os.getenv('AV_SCAN_URL')

    # The factor used to determine how long to wait before retrying failed scans
    # NOTE: This value exponentially increases up to the maximum retries allowed
    # algo: {backoff factor} * (2 ** ({number of total retries} - 1))
    AV_SCAN_BACKOFF_FACTOR = os.getenv('AV_SCAN_BACKOFF_FACTOR', 1)

    # The maximum number of times to retry failed virus scans
    AV_SCAN_MAX_RETRIES = os.getenv('AV_SCAN_MAX_RETRIES', 5)

    # The number of seconds to wait for socket response from clamav-rest
    AV_SCAN_TIMEOUT = os.getenv('AV_SCAN_TIMEOUT', 30)

    ###
    # Authentication Provider Settings
    #
    LOGIN_GOV_ACR_VALUES = os.getenv(
        'ACR_VALUES',
        'http://idmanagement.gov/ns/assurance/ial/1'
    )
    LOGIN_GOV_AUTHORIZATION_ENDPOINT = None
    LOGIN_GOV_CLIENT_ASSERTION_TYPE = os.getenv(
        'CLIENT_ASSERTION_TYPE',
        'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
    )
    LOGIN_GOV_CLIENT_ID = os.getenv(
        'CLIENT_ID',
        'urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev'
    )
    LOGIN_GOV_ISSUER = None
    LOGIN_GOV_JWKS_ENDPOINT = None
    LOGIN_GOV_LOGOUT_ENDPOINT = None
    LOGIN_GOV_MOCK_TOKEN = os.getenv(
        'MOCK_TOKEN',
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiMmQyZDExNS0xZDdlLTQ1'
        'NzktYjlkNi1mOGU4NGY0ZjU2Y2EiLCJpc3MiOiJodHRwczovL2lkcC5pbnQubG9naW4uZ2'
        '92IiwiYWNyIjoiaHR0cDovL2lkbWFuYWdlbWVudC5nb3YvbnMvYXNzdXJhbmNlL2xvYS8x'
        'Iiwibm9uY2UiOiJhYWQwYWE5NjljMTU2YjJkZmE2ODVmODg1ZmFjNzA4MyIsImF1ZCI6In'
        'Vybjpnb3Y6Z3NhOm9wZW5pZGNvbm5lY3Q6ZGV2ZWxvcG1lbnQiLCJqdGkiOiJqQzdOblU4'
        'ZE5OVjVsaXNRQm0xanRBIiwiYXRfaGFzaCI6InRsTmJpcXIxTHIyWWNOUkdqendsSWciLC'
        'JjX2hhc2giOiJoWGpxN2tPcnRRS196YV82dE9OeGN3IiwiZXhwIjoxNDg5Njk0MTk2LCJp'
        'YXQiOjE0ODk2OTQxOTgsIm5iZiI6MTQ4OTY5NDE5OH0.pVbPF2LJSG1fE9thn27PwmDlNd'
        'lc3mEm7fFxb8ZADdRvYmDMnDPuZ3TGHl0ttK78H8NH7rBpH85LZzRNtCcWjS7QcycXHMn0'
        '0Cuq_Bpbn7NRdf3ktxkBrpqyzIArLezVJJVXn2EeykXMvzlO-fJ7CaDUaJMqkDhKOK6caR'
        'YePBLbZJFl0Ri25bqXugguAYTyX9HACaxMNFtQOwmUCVVr6WYL1AMV5WmaswZtdE8POxYd'
        'hzwj777rkgSg555GoBDZy3MetapbT0csSWqVJ13skWTXBRrOiQQ70wzHAu_3ktBDXNoLx4'
        'kG1fr1BiMEbHjKsHs14X8LCBcIMdt49hIZg'
    )
    LOGIN_GOV_TOKEN_ENDPOINT = None


os.environ.setdefault(
    "OIDC_OP_AUTHORIZATION_ENDPOINT",
    "https://idp.int.identitysandbox.gov/openid_connect/authorize"
)
os.environ.setdefault("OIDC_OP_ISSUER", "https://idp.int.identitysandbox.gov/")
os.environ.setdefault(
    "OIDC_OP_JWKS_ENDPOINT",
    "https://idp.int.identitysandbox.gov/api/openid_connect/certs"
)
os.environ.setdefault(
    "OIDC_OP_LOGOUT_ENDPOINT",
    "https://idp.int.identitysandbox.gov/openid_connect/logout"
)
os.environ.setdefault(
    "OIDC_OP_TOKEN_ENDPOINT",
    "https://idp.int.identitysandbox.gov/api/openid_connect/token"
)
