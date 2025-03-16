from flask_wtf import FlaskForm
from wtforms import (StringField, DateField, TextAreaField,
                     RadioField, IntegerField, FloatField,
                     SelectMultipleField, FileField, SelectField)
from wtforms.fields.simple import PasswordField
from wtforms.validators import (DataRequired, Length, NumberRange,
                                EqualTo, ValidationError)
import re


# register the user
class RegisteForm(FlaskForm):
    # Field for the username
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1, 20)])
    # Field for the password
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(8, 15)])
    avatar = FileField('Avatar', validators=[DataRequired()])


# user login
class LoginForm(FlaskForm):
    # Field for the username
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1, 20)])
    # Field for the password
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(8, 15)])


# post the comment and rate the movie
class EvaluateForm(FlaskForm):
    comment = TextAreaField('comment',
                            validators=[DataRequired(),
                                        Length(1, 300)])
    rating = RadioField(
        'rating',
        choices=[
            ('10', '10 stars'),
            ('9', '9 stars'),
            ('8', '8 stars'),
            ('7', '7 stars'),
            ('6', '6 stars'),
            ('5', '5 stars'),
            ('4', '4 stars'),
            ('3', '3 stars'),
            ('2', '2 star'),
            ('1', '1 stars')
        ],
        validators=[DataRequired(message="Please rate.")]
    )


# change the username in my account
class ChangeUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1, 20)])


# change the password in my account
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password',
                                     validators=[DataRequired(),
                                                 Length(8, 15)])
    newpassword = PasswordField('New Password',
                                validators=[DataRequired(),
                                            Length(8, 15)])
    confirm_newpassword = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('newpassword',
                                message="Passwords must match.")])


# ensure that it is at most one decimal place
def validate_one_decimal(form, field):
    value = str(field.data)
    if not re.match(r'^\d(\.\d)?$', value):
        raise (ValidationError
               ("Rating must be a decimal with at most one decimal place."))


# administrator create movie
class CreateMovieForm(FlaskForm):
    # Field for the title of the movie
    movie_title = StringField('Movie Title',
                              validators=[DataRequired(),
                                          Length(1, 70)])
    # Field for the release date
    release_date = DateField('Release Date',
                             validators=[DataRequired()])

    # Field for providing a description of the assessment
    overview = TextAreaField('Overview',
                             validators=[DataRequired()])
    tagline = TextAreaField('Tagline',
                            validators=[DataRequired()])
    director = StringField('Director',
                           validators=[DataRequired(),
                                       Length(1, 100)])
    spoken_languages = StringField('Languages',
                                   validators=[DataRequired(),
                                               Length(1, 100)])
    certificate = StringField('Certificate',
                              validators=[DataRequired(),
                                          Length(1, 10)])
    star1 = StringField('Star1',
                        validators=[DataRequired(),
                                    Length(1, 30)])
    star2 = StringField('Star2',
                        validators=[DataRequired(),
                                    Length(1, 30)])
    # Field for runtime (in minutes)
    runtime = IntegerField(
        'Runtime',
        validators=[DataRequired(),
                    NumberRange(min=1,
                                message="Runtime must be greater than 0")])

    # Field for backdrop image path
    backdrop_path = StringField('Backdrop Image Path',
                                validators=[DataRequired(), Length(1, 100)])

    # Field for poster image path
    poster_path = StringField('Poster Image Path',
                              validators=[DataRequired(), Length(1, 100)])

    # Field for average rating
    average_rating = FloatField(
        'Average Rating',
        validators=[NumberRange
                    (min=0,
                     max=10,
                     message="Rating must be between 0 and 10"),
                    validate_one_decimal])

    # Field for genres (select multiple genres)
    genres = SelectMultipleField('Genres',
                                 choices=[('Action', 'Action'),
                                          ('Adventure', 'Adventure'),
                                          ('Animation', 'Animation'),
                                          ('Comedy', 'Comedy'),
                                          ('Crime', 'Crime'),
                                          ('Drama', 'Drama'),
                                          ('Family', 'Family'),
                                          ('Fantasy', 'Fantasy'),
                                          ('History', 'History'),
                                          ('Horror', 'Horror'),
                                          ('Music', 'Music'),
                                          ('Mystery', 'Mystery'),
                                          ('Romance', 'Romance'),
                                          ('Sci-Fi',
                                           'Sci-Fi'),
                                          ('Thriller', 'Thriller'),
                                          ('War', 'War'),
                                          ('Western', 'Western')],
                                 validators=[DataRequired()])


# administrator manage user
class ManageUserForm(FlaskForm):
    avatar = StringField('Avatar', validators=[DataRequired(), Length(1, 120)])
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1, 20)])
    # role
    role = SelectField('Role',
                       validators=[DataRequired()],
                       choices=[('admin', 'admin'), ('user', 'user')])
    # favorites
    favorite_movies = StringField('Favorite Movies',
                                  validators=[DataRequired()])
    # status
    is_active = SelectField('Allow Login',
                            validators=[DataRequired()],
                            choices=[(1, 'Yes'), (0, 'No')])


# administrator manage genre
class ManageGenreForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 15)])
