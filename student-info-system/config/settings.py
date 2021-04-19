import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if os.getenv('PRODUCTION') and not os.getenv('GITHUB_WORKFLOW'):
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG')
else:
    SECRET_KEY = "(abaz)3wml_wsqh^02#*=47psn=r1!dfx=q9g*cspm(j)5@*$a"
    DEBUG = True

# TODO: Set up ALLOWED_HOSTS for production env in settings
if os.getenv('PRODUCTION'):
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["*"]

# APPLICATION DEFINITION
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    'debug_toolbar',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "bootstrap3",
    "phone_field",
    "django_tables2",
    "django_filters",
    "sis",
    "student",
    "professor",
    "schooladmin",
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
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

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/sis'

# STATIS FILES (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEBUG_TOOLBAR_CONFIG = {
    # COMMENT OUT this line to ENABLE debug toolbar
    # UNCOMMENT this line to DISABLE debug toolbar
    'SHOW_TOOLBAR_CALLBACK': lambda r: False,
    'SHOW_COLLAPSED': True,
    'SQL_WARNING_THRESHOLD': 100,
}

INTERNAL_IPS = [
    '127.0.0.1',
]

WSGI_APPLICATION = "config.wsgi.application"

# DATABASE
# We have our development database db.sqlite3, our Github db, and production db using postgresql.
# GITHUB_WORKFLOW env variable is only available in GitHub Actions. So in actions
# we want a simple postgres docker image to be booted as a service and does all the testing there.

# When we deploy to cloud the else block will work as we won't be having GITHUB_WORKFLOW env var
# in our deployment. That time the db config we use DB_USER, DB_NAME, DB_PASSWORD, DB_HOST and
# DB_PASSWORD which we will set in repository secret to be used in our deployment.

if os.getenv('PRODUCTION'):
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
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# INTERNATIONALIZATION
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Log all SQL to console...uncomment this.
# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     }
# }
