# Configuring SQLite
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'movieRS.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True


# Enable the CSRF prevention function
WTF_CSRF_ENABLED = True
SECRET_KEY = 'this-is-a-very-secret-secret'
