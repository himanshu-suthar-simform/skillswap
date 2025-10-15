from .base import *  # noqa

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Static files finder configuration
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files (User uploaded files)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Ensure media and static directories exist
# NOTE: The media root and static files are only needed for local development purpose.
# We need to remove this in production and use file service and route it to it through proxy services.
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
