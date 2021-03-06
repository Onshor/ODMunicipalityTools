# project/config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""

    # main config
    SECRET_KEY = 'my_precious'
    SECURITY_PASSWORD_SALT = 'saltsercretmunicipal%%onshor'
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = 'onshor.mail.contact@gmail.com'
    MAIL_PASSWORD = 'onshorPWD17%%'

    # mail accounts
    MAIL_DEFAULT_SENDER = 'onshor.mail.contact@gmail.com'

    # ckan_config
    CKAN_URL = 'http://openbaladiati.tn/'
    CKAN_API_KEY = '86e646dd-6edc-4aeb-989e-f67246510e9e'


class DevelopmentConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SECURITY_PASSWORD_SALT = "saltsercretmunicipal%%onshor"
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/municipal_db_test2_0"
    SQLALCHEMY_DATABASE_URI = "postgresql://municipality:municipality@localhost/municipal_db"
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_SECRET_KEY = 'foo'
    STRIPE_PUBLISHABLE_KEY = 'bar'


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SECURITY_PASSWORD_SALT = "saltsercretmunicipal%%onshor"
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/municipal_db_test2_0"
    SQLALCHEMY_DATABASE_URI = "postgresql://municipality:municipality@localhost/municipal_db"
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_SECRET_KEY = 'foo'
    STRIPE_PUBLISHABLE_KEY = 'bar'
