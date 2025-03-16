from app import db, app

# Creates all the tables and the database.
with app.app_context():
    db.create_all()
