import os

# Set the base directory for the database
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = '\xa2\xf4\xde%\x1a\xa0\xb4\xa2\xc8/\xa6\xff\x05Q\xb8/\xda\x9b\xa6\x19\xba\\o\x81'
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')

config_by_name = dict(
    dev = DevelopmentConfig,
    test = TestingConfig,
    prod = ProductionConfig
)
