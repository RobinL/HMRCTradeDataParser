from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension


bootstrap = Bootstrap()
db = SQLAlchemy()
toolbar = DebugToolbarExtension()

from flask import Blueprint
myapp = Blueprint('myapp', __name__)
from . import views

from config import config


from flask import Flask
def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])


    bootstrap.init_app(app)
    db.init_app(app)

    if config_name == "development":
    	toolbar = DebugToolbarExtension(app)


    app.register_blueprint(myapp)

    return app


