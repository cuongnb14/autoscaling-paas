from .common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autoscaling',
        'USER': 'root',
        'PASSWORD': 'galaxy',
        'HOST': '10.10.10.51',
        'PORT': '31102',
    }
}

INFLUXDB = {
    "HOST": "10.10.10.51",
    "PORT" : "31101",
    "USERNAME" : "root",
    "PASSWORD" : "root",
    "DBNAME" : "autoscaling",
}
