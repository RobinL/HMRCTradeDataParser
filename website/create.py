
from flask.ext.sqlalchemy import SQLAlchemy
from myapp import create_app
from myapp import models
app = create_app("development")
from myapp import db
with app.app_context():
    db.create_all()