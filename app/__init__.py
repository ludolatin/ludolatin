from flask import Flask, redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db=db)
    login_manager.init_app(app)

    from .quiz import quiz as quiz_blueprint
    app.register_blueprint(quiz_blueprint)

    from .dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    from .topic import topic as topic_blueprint
    app.register_blueprint(topic_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .utils import utils as utils_blueprint
    app.register_blueprint(utils_blueprint)

    from .store import store as store_blueprint
    app.register_blueprint(store_blueprint)

    class AuthenticatedAdminIndex(AdminIndexView):
        @expose('/')
        def index(self):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            if not current_user.is_admin:
                return redirect(url_for('dashboard.dashboard'))
            return super(AuthenticatedAdminIndex, self).index()

    # Initialise flask-admin
    from app.models import User, Answer, Sentence, Language, Quiz, Score, Topic, Product, Purchase
    admin = Admin(
        app,
        name='LudoLatin',
        template_mode='bootstrap3',
        base_template='admin_base.html',
        index_view=AuthenticatedAdminIndex()
    )

    class AuthenticatedModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            # redirect to login page if user doesn't have access
            return redirect(url_for('auth.login', next=request.url))

        column_exclude_list = ('password_hash')

    # Add administrative views here
    admin.add_view(AuthenticatedModelView(User, db.session))
    admin.add_view(AuthenticatedModelView(Language, db.session))
    admin.add_view(AuthenticatedModelView(Topic, db.session, endpoint="admin_topic"))
    admin.add_view(AuthenticatedModelView(Quiz, db.session, endpoint="admin_quiz"))
    admin.add_view(AuthenticatedModelView(Sentence, db.session))
    admin.add_view(AuthenticatedModelView(Answer, db.session))
    admin.add_view(AuthenticatedModelView(Score, db.session))
    admin.add_view(AuthenticatedModelView(Product, db.session))
    admin.add_view(AuthenticatedModelView(Purchase, db.session))

    return app
