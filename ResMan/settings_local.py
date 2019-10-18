# coding=utf-8
# Do not overwrite `settings.py` files, instead of rename this file to `settings_local.py` and specify your custom
# settings in it

import os
import sys

APP_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, APP_DIR)
globals().update(vars(sys.modules['ResMan.settings']))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


AUTH_PASSWORD_VALIDATORS =[
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
    {
        'NAME': 'CustomUser.password_validation.RepeatPasswordAmount',
        'OPTIONS':{
            'num_amount':3
        }
    },
    {
        'NAME': 'CustomUser.password_validation.MinimumNumAmount',
    },
    {
        'NAME': 'CustomUser.password_validation.MinimumUpperLetterAmount',
    },
    {
        'NAME': 'CustomUser.password_validation.MinimumSymbolAmount',
    },
]
