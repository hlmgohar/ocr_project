import os 
from .settings import *
from .settings import BASE_DIR


SECRET_KEY = os.environ['SECRET']
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']]
DEBUG = False

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Should be placed at the top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['AZURE_MYSQL_NAME'],            # Your database name
        'USER': os.environ['AZURE_MYSQL_USER'],       # Your MySQL username
        'PASSWORD': os.environ['AZURE_MYSQL_PASSWORD'],   # Your MySQL password
        'HOST': os.environ['AZURE_MYSQL_HOST'],           # Database host, e.g., localhost or an IP
    'OPTIONS': {
            'charset': 'utf8mb4',  # Add this line
    },
    }
}
