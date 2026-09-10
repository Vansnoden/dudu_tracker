from .base import *


config = {
    'DB_NAME': os.getenv('POSTGRES_DB'),
    'DB_USER': os.getenv('POSTGRES_USER'),
    'DB_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'DB_HOST': os.getenv('DB_HOST'),
    'DB_PORT': os.getenv('DB_PORT'),
    'WEB_DOMAIN': os.getenv('WEB_DOMAIN')
}

DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS=[
    "https://dudutracker.monadeware.com", 
    "http://dudutracker.monadeware.com", 
    "http://dudutracker.monadware.com", 
    "https://dudutracker.monadware.com", 
    "http://dudutracker.icipe.org",
    "https://dudutracker.icipe.org"
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config['DB_NAME'],
        'USER': config['DB_USER'],
        'PASSWORD': config['DB_PASSWORD'],
        'HOST': config['DB_HOST'],
        'PORT': config['DB_PORT']
    }
}

