from .common import * 

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autoscaling',
        'USER': 'root',
        'PASSWORD': 'galaxy',
        'HOST': '127.0.0.1',
        'PORT': '43306',
    }
}
