from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'task17',
        'USER': 'test',
        'PASSWORD': '12',
        'HOST': os.environ.get('HOST'),
        'PORT': '5432',
    }
}