from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
# Handles all migrations.
migrate = Migrate(app, db)

from app import views, models  # noqa: F401, E402
