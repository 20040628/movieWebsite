from app import db
from datetime import datetime

# many-to-many relationships between users and favorite movies
user_movie_favorite = db.Table('user_movie_favorite',
                               db.Column('user_id',
                                         db.Integer,
                                         db.ForeignKey('user.id'),
                                         primary_key=True),
                               db.Column('movie_id',
                                         db.Integer,
                                         db.ForeignKey('movie.id'),
                                         primary_key=True))

# many-to-many relationships between genres and movies
movie_genre = db.Table('movie_genre',
                       db.Column('movie_id',
                                 db.Integer,
                                 db.ForeignKey('movie.id'),
                                 primary_key=True),
                       db.Column('genre_id',
                                 db.Integer,
                                 db.ForeignKey('genre.id'),
                                 primary_key=True))


# store movies
class Movie(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_title = db.Column(db.String(70), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    overview = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.Text, nullable=False)
    backdrop_path = db.Column(db.String(100), nullable=False)
    poster_path = db.Column(db.String(100), nullable=False)
    spoken_languages = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    average_rating = db.Column(db.Float, nullable=False)
    certificate = db.Column(db.String(10), nullable=False)
    star1 = db.Column(db.String(30), nullable=False)
    star2 = db.Column(db.String(30), nullable=False)
    genres = db.relationship('Genre', secondary=movie_genre,
                             backref='belong_genre')


# store user
class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    favorite_movies = db.relationship('Movie',
                                      secondary=user_movie_favorite,
                                      backref='users_who_favorite')
    avatar = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Integer, nullable=False, default=1)


# store genre
class Genre(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(15), nullable=False)


# store user log
class UserLog(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow().replace(microsecond=0))
    user = db.relationship('User', backref=db.backref('logs', lazy=True))


# store user evaluate
class Evaluate(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)
    submit_date = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow().replace(microsecond=0))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('reviews', lazy=True))
