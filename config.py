import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def create_sqlite_uri(db_name):
    return 'sqlite:///' + os.path.join(BASEDIR, db_name)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key, just for testing'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299

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
