# -*- coding: utf-8 -*-
# secret settings
from mongoengine import connect

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_PATCH_SETTINGS = False

connect('sfchat', host='localhost', port=27017, username='', password='')

SECRET_KEY = '111!ebrl5h61ztet=c&ydh+sc9tkq=b70^xbx461)l1pp!l000'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
        #~ 'USER': '',
        #~ 'PASSWORD': '',
        #~ 'HOST': '',
        #~ 'PORT': '',
    }
}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

ADMINS = (
    ('admin', 'info@mysmile.com.ua'),
)
#
# MANAGERS = (
#     ('admin', 'info@mysmile.com.ua'),
# )

