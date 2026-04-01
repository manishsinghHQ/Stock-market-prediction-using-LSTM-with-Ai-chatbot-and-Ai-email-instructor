from pathlib import Path
import environ, os, datetime




BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='dev-secret-key')
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = [h.strip() for h in env('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'accounts',
    'dashboard',
    'pages'
    
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

ROOT_URLCONF = 'stockai_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'stockai_project.wsgi.application'

# Database (SQLite by default, switch to MySQL with DATABASE_URL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth/session
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", 60 * 60 * 24 * 30))  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# DeepSeek via OpenRouter
OPENROUTER_API_KEY=env("OPENROUTER_API_KEY")
OPENROUTER_MODEL = env("OPENROUTER_MODEL", default="arcee-ai/trinity-large-preview:free")

OPENROUTER_BASE_URL = env("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1/chat/completions")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD") # use App Password (not Gmail password)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

