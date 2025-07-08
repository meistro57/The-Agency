import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'replace-this'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]
ROOT_URLCONF = 'interfaces.django_dashboard.dashboard.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]
WSGI_APPLICATION = 'interfaces.django_dashboard.dashboard.wsgi.application'
STATIC_URL = '/static/'
