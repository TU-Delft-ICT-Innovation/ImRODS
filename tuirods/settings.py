"""
Django settings for irods project.

Generated by 'django-admin startproject' using Django 1.11.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from kombu import Exchange, Queue

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import saml2
from saml2 import BINDING_HTTP_REDIRECT, BINDING_URI
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_SOAP
from saml2.saml import NAME_FORMAT_URI
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import NAMEID_FORMAT_PERSISTENT

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm=cof8t_ycw#h4e4xw^2)y^l7#5q8s)kdrz96u^hkawo2!sh94'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG_STR = os.environ.get('DEBUG', 'True')
DEBUG = DEBUG_STR == 'True'

admins = os.environ.get('ADMINS', "(('Marcel Heijink', 'm.j.heijink@tudelft.nl'),)")
ADMINS = eval(admins)
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'root@irods.tudelft.nl')
EMAIL_FROM = u'Irods'
ERROR_EMAIL = ''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'dutmail.tudelft.nl'
EMAIL_HOST_USER = 'noreply@tudelft.nl'
EMAIL_PORT = 25

SESSION_EXPIRE_SECONDS = 100

ALLOWED_HOSTS = ['irods.tudelft.nl']

SUIT_CONFIG = {
    'ADMIN_NAME': os.environ.get('SUIT_TITLE', 'IRODS'),

    'HEADER_DATE_FORMAT': 'l, j. F Y',  # Saturday, 16th March 2013
    'HEADER_TIME_FORMAT': 'H:i:s',        # 18:42
    
    'SHOW_REQUIRED_ASTERISK': True

}



# Application definition

INSTALLED_APPS = [
    'irodsapp',
    'suit',
    #'django.contrib.admin',
    'django.contrib.admin.apps.SimpleAdminConfig',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_celery_beat',
    'djangosaml2',
]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tuirods.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tuirods.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'irods'),
        'USER': os.environ.get('DB_USER', 'irods'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'irods'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB;SET sql_mode="STRICT_TRANS_TABLES"'
        }
    },
}



AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
)

# -----SAML -----
LOGIN_URL = '/saml2/login/'
LOGOUT_URL = '/saml2/logout/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',
 
    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': os.environ.get('ENTITYID', 'https://irods.tudelft.nl'),
 
    # directory with attribute mapping
    'attribute_map_dir': os.path.join(BASE_DIR, 'saml/attribute-maps'),
    'allow_unknown_attributes': False,
 
    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp': {
            'name': 'Irods',
            'name_id_format': NAMEID_FORMAT_PERSISTENT,
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('https://irods.tudelft.nl/saml2/acs/',
                     BINDING_HTTP_POST),
                ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    ('https://irods.tudelft.nl/saml2/ls/',
                     BINDING_HTTP_REDIRECT),
                ],
            },
                
 
            # attributes that this project need to identify a user
            'required_attributes': ['uid', 'sn', 'mail'],
            'authn_requests_signed': True,
            'want_assertions_signed': False,
            'want_responses_signed': True,
 
            'allow_unknown_attributes': False,
        },
    },
 
    # where the remote metadata is stored
    'metadata': {
        'local': ['/etc/saml/metadata.xml'],
    },
 
    # set to 1 to output debugging information
    'debug': 1,
 
    # certificate
    'key_file': '/etc/saml/saml.key',  # private part
    'cert_file': '/etc/saml/saml.crt',  # public part
 
    # own metadata settings
    'contact_person': [
        {'given_name': 'Marcel',
         'sur_name': 'Heijink',
         'company': 'TU Delft',
         'email_address': 'm.j.heijink@tudelft.nl',
         'contact_type': 'technical'},
    ],
    # you can set multilanguage information here
    'organization': {
        'name': [('TU Delft', 'nl'), ('University of Technology', 'en')],
        'display_name': [('TU Delft', 'nl'), ('TU Delft', 'en')],
        'url': [('http://www.tudelft.nl', 'nl'), ('http://www.tudelft.nl', 'en')],
    },
    # 'valid_for': 24,  # how long is our metadata valid
}
 
 
SAML_ATTRIBUTE_MAPPING = {
    'urn:mace:dir:attribute-def:uid': ('username',),
    'urn:mace:dir:attribute-def:mail': ('email',),
}
 
SAML_CREATE_UNKNOWN_USER = False
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'username'








# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

LOG_DIR = '/var/log/supervisor'
 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(process)d %(thread)d  %(message)s'
        },
        'timestamped': {
            'format': '%(asctime)s %(levelname)s %(name)s  %(message)s'
        },
        'simple': {
            'format': '%(levelname)s  %(message)s'
        },
        'performance': {
            'format': '%(asctime)s %(process)d | %(thread)d | %(message)s',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'djangosaml2.log'),
            'formatter': 'timestamped',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
 
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'djangosaml2': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
 
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         },        
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/



STATIC_URL = '/static/'
STATIC_ROOT = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'templates', 'static'),
]



# Redis
#REDIS_PORT = 6379
#REDIS_DB = 0
#REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'redis')
RABBIT_HOSTNAME = os.environ.get('RABBIT_PORT_5672_TCP', 'rabbit')
if RABBIT_HOSTNAME.startswith('tcp://'):
    RABBIT_HOSTNAME = RABBIT_HOSTNAME.split('//')[1]
BROKER_URL = os.environ.get('BROKER_URL',
                            '')
if not BROKER_URL:
    BROKER_URL = 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=os.environ.get('RABBIT_ENV_USER', 'admin'),
        #user='admin1',
        password=os.environ.get('RABBIT_ENV_RABBITMQ_PASS', 'mypass'),
        hostname=RABBIT_HOSTNAME,
        vhost=os.environ.get('RABBIT_ENV_VHOST', ''))
# We don't want to have dead connections stored on rabbitmq, so we have to negotiate using heartbeats
BROKER_HEARTBEAT = '?heartbeat=30'
if not BROKER_URL.endswith(BROKER_HEARTBEAT):
    BROKER_URL += BROKER_HEARTBEAT
BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10
# Celery configuration
# configure queues, currently we have only one
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)
# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False
 
# By default we will ignore result
# If you want to see results and try out tasks interactively, change it to False
# Or change this setting on tasks level
CELERY_IGNORE_RESULT = False
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600
 
# Set redis as celery result backend
#CELERY_RESULT_BACKEND = 'redis://%s:%d/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
#CELERY_REDIS_MAX_CONNECTIONS = 1
 
# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']
 
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 1000
 
 
CELERY_TASK_RESULT_EXPIRES = 7*86400  # 7 days
# needed for worker monitoring
CELERY_SEND_EVENTS = True
# where to store periodic tasks (needed for scheduler)
#CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_RESULT_BACKEND = 'django-db'

