import os

# Flask configuration
DEBUG = True
SECRET_KEY = os.urandom(24)

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = ''

# Flask-Mail configuration
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
DEFAULT_MAIL_SENDER = None