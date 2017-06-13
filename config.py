import os

database_username = os.environ.get('DATABASE_USERNAME') or 'root'
database_password = os.environ.get('DATABASE_PASSWORD') or ''

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key, just for testing'

    # SQLAlchemy settings
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

    # Flask-Blogging sessiongs
    BLOGGING_URL_PREFIX = "/articles"
    BLOGGING_SITEURL = "https://www.ludolatin.com"
    BLOGGING_SITENAME = "LudoLatin"
    BLOGGING_PERMISSIONS = True
    BLOGGING_PLUGINS = ["blogging_plugins.tag_cloud", "blogging_plugins.summary"]
    FILEUPLOAD_IMG_FOLDER = "fileupload"
    FILEUPLOAD_PREFIX = "/fileupload"
    FILEUPLOAD_ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="root",
        password="",
        hostname="localhost",
        databasename="ludolatin_dev",
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="root",
        password="",
        hostname="localhost",
        databasename="ludolatin_test",
    )
    WTF_CSRF_ENABLED = False
    import logging
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    )
    logging.getLogger().setLevel(logging.DEBUG)


class PreProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username=database_username,
        password=database_password,
        hostname="ingenuity.mysql.pythonanywhere-services.com",
        databasename="ingenuity$preproduction",
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username=database_username,
        password=database_password,
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
