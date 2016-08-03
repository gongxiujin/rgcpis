from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_themes2 import Themes
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
themes = Themes()
migrate = Migrate()
