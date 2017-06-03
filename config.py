import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key, just for testing'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"LudoLatin" <noreply@ludolatin.com>')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="root",
        password="",
        hostname="localhost",
        databasename="ingenuity_dev",
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="root",
        password="",
        hostname="localhost",
        databasename="ingenuity_test",
    )
    WTF_CSRF_ENABLED = False
    import logging
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    )
    logging.getLogger().setLevel(logging.DEBUG)


class PreProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="ingenuity",
        password="LudoLatin",
        hostname="ingenuity.mysql.pythonanywhere-services.com",
        databasename="ingenuity$preproduction",
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="ingenuity",
        password="LudoLatin",
        hostname="ingenuity.mysql.pythonanywhere-services.com",
        databasename="ingenuity$production",
    )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'preproduction': PreProductionConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
