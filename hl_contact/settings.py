from pathlib import Path
import os
import environ


env = environ.Env()

# reading .env file
environ.Env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
TOKEN = env("TOKEN")
EMAIL = env("EMAIL")
EMAIL_PASSWORD = env("EMAIL_PASSWORD")
USER_EMAIL = env("USER_EMAIL")
USER_EMAIL_PASSWORD = env("USER_EMAIL_PASSWORD")
CLIENT_ID = env("CLIENT_ID")
CLIENT_SECRET = env("CLIENT_SECRET")
CALLBACK_URL = env("CALLBACK_URL")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
DB_NAME = env("DB_NAME")
DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")
DEBUG = env("DEBUG")


ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "django_filters",
    "subaccounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hl_contact.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "hl_contact.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Google Cloud Storage for Static File Serve
GS_PROJECT_ID = env("GS_PROJECT_ID")
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
GS_AUTO_CREATE_BUCKET = True
GS_DEFAULT_ACL = "publicRead"

# STATIC_URL = "https://storage.googleapis.com/{}/".format(GS_BUCKET_NAME)

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static_root/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5173",
    "https://fua.vercel.app",
    "https://hl-admin.vercel.app",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}


SITE_ID = 1
LOGIN_REDIRECT_URL = "/"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"
AUTH_USER_MODEL = "subaccounts.CustomUser"


REST_AUTH = {
    "REGISTER_SERIALIZER": "subaccounts.serializers.CustomRegisterSerializer",
    "LOGIN_SERIALIZER": "subaccounts.serializers.CustomLoginSerializer",
    "USER_DETAILS_SERIALIZER": "subaccounts.serializers.CustomUserSerializer",
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,  # Add this to disable session authentication
}

# STORAGES = {
#     "default": {
#         "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
#     },
# }

if not DEBUG:
    CSRF_TRUSTED_ORIGINS = ["https://hl-contact-qh6kcxvdja-uc.a.run.app"]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
