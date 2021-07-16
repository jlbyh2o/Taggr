import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect()
csrf.init_app(app)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'taggr.sqlite'),
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'taggr.sqlite'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'

from . import auth
app.register_blueprint(auth.bp)

from . import main
app.register_blueprint(main.bp)
app.add_url_rule('/', endpoint='index')

from . import models
