import os
from app import app, db
from flask import (render_template, flash, redirect,
                   url_for, request, jsonify, session)
from werkzeug.security import generate_password_hash, check_password_hash
from .models import (UserLog, Movie, User, user_movie_favorite, Genre,
                     Evaluate, movie_genre)
from .forms import (RegisteForm, LoginForm, EvaluateForm,
                    CreateMovieForm, ChangeUserForm, ChangePasswordForm,
                    ManageGenreForm, ManageUserForm)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename
from urllib.parse import quote
import re


def log_user_action(user_id, action, description=None):
    user_log = UserLog(user_id=user_id, action=action, description=description)
    db.session.add(user_log)
    db.session.commit()


# Route for the home page
@app.route('/')
def index():
    app.logger.info("The homepage page is requested")
    try:
        # top three movies
        top_movies = Movie.query.order_by(
            Movie.average_rating.desc()).limit(3).all()

        # 6 movies
        movie_list = Movie.query.order_by(Movie.id.asc()).limit(8).all()

        # latest movie
        latest_movie = Movie.query.order_by(Movie.release_date.desc()).first()
        return render_template('index.html',
                               title='MetaCritic',
                               top_movies=top_movies,
                               movie_list=movie_list,
                               latest_movie=latest_movie)
    except Exception as e:
        app.logger.error(f"An error appears when loading the home page：{str(e)}")


@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info("The login page is requested")
    try:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if not user:
                flash('The current user name does not exist', 'error')
                return redirect(url_for('login'))
            # Check whether the password is correct
            if check_password_hash(user.password, form.password.data):
                is_active = user.is_active
                session['is_active'] = is_active
                if is_active == 0:
                    flash('Your account is disabled by the administrator.',
                          'error')
                    log_user_action(user.id, 'login_failed',
                                    "User account is disabled.")
                    return redirect(url_for('login'))
                session['logged_in'] = True
                session['username'] = user.username
                session['userid'] = user.id
                role = user.role
                session['role'] = role
                log_user_action(user.id, 'login',
                                'User logged in successfully.')
                # determine the role of the user
                if role == 'user':
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('manageMovie'))

            else:
                flash('Incorrect password.', 'error')
                log_user_action(user.id, 'login_failed',
                                "User logged in with wrong password.")
                return redirect(url_for('login'))
        return render_template('login.html',
                               title='Login',
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the login page：{str(e)}")


@app.route('/logout')
def logout():
    user_id = session.get('userid')
    log_user_action(user_id, 'logout', 'User logged out.')
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userid', None)
    session.pop('role', None)
    return redirect(url_for('index'))


# register an account
@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.info("The register page is requested")
    try:
        form = RegisteForm()
        if form.validate_on_submit():
            # Ensure username is unique
            existing_username = User.query.filter_by(
                username=form.username.data).first()
            if existing_username:
                flash('Create failure! This user name'
                      ' is already in use.', 'error')
                return redirect(url_for('register'))
            else:
                # encrypted password
                hashed_password = generate_password_hash(form.password.data,
                                                         method='pbkdf2:sha256')

                # handle the avatar
                if form.avatar.data:
                    avatar = form.avatar.data
                    avatar_filename = secure_filename(quote(avatar.filename))
                    # Check file extension
                    if '.' not in avatar_filename:
                        flash('Invalid file: Only JPG, PNG, or JPEG files '
                              'are allowed.', 'error')
                        return redirect(url_for('register'))

                    if (avatar_filename.rsplit('.', 1)[1].lower()
                            not in ['jpg', 'jpeg', 'png']):
                        flash('Invalid file. Only JPG, PNG, or JPEG files'
                              ' are allowed.', 'error')
                        return redirect(url_for('register'))
                    file_path = os.path.join('app/static/img/avatars',
                                             avatar_filename)
                    avatar.save(file_path)

                new_user = User(
                    username=form.username.data,
                    password=hashed_password,
                    avatar=avatar_filename
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Create successfully.', 'success')
                user = User.query.filter_by(username=form.username.data).first()
                log_user_action(user.id, 'Register', "User registered.")
                return redirect(url_for('register'))
        return render_template('register.html',
                               title='Register',
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the register page：{str(e)}")


@app.route('/account', methods=['GET', 'POST'])
def account():
    app.logger.info("The account page is requested")
    try:
        # Only login and is active
        userid = session.get('userid')
        username = session.get('username')
        if userid is None:
            return redirect(url_for('login'))
        role = session.get('role')
        if (role == 'admin'):
            return redirect(url_for('manageMovie'))
        user = User.query.filter_by(id=userid).first()
        is_active = user.is_active
        if is_active == 0:
            return redirect(url_for('logout'))

        form = ChangeUserForm()
        if form.validate_on_submit():
            # Handle the username change
            new_username = form.username.data
            # Check if the new username is changed
            if new_username == username:
                flash('You do not change the username.', 'error')
            # Check if the new username already exists
            else:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    flash('Username already taken, '
                          'please choose another one.', 'error')
                else:
                    # Update the user's username in the database
                    user.username = new_username
                    db.session.commit()
                    session['username'] = new_username
                    log_user_action(userid,
                                    'change username',
                                    'user {} change the username to {}.'.format(
                                        userid, new_username))
                    flash('Username updated successfully!', 'success')

            return redirect(url_for('account'))

        return render_template('account.html',
                               title='Account',
                               user=user,
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the account page：{str(e)}")


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    app.logger.info("The change_password page is requested")
    try:
        # Only login and is active
        userid = session.get('userid')
        if userid is None:
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(id=userid).first()
            is_active = user.is_active
            if is_active == 0:
                return redirect(url_for('logout'))
        role = session.get('role')
        if (role == 'admin'):
            return redirect(url_for('manageMovie'))
        form = ChangePasswordForm()
        if form.validate_on_submit():
            # Check whether the current password is correct
            current_password = form.current_password.data
            if not check_password_hash(user.password, current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('change_password'))

            # Check whether the new password matches the confire password
            new_password = form.newpassword.data
            confirm_newpassword = form.confirm_newpassword.data
            if new_password != confirm_newpassword:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('change_password'))

            # update password
            hashed_new_password = generate_password_hash(new_password)
            user.password = hashed_new_password
            db.session.commit()
            log_user_action(userid, 'change password',
                            'user {} change the password.'.format(userid))
            flash('Password updated successfully.', 'success')
            return redirect(url_for('change_password'))

        return render_template('accountPassword.html',
                               title='Account',
                               user=user,
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the change password page：{str(e)}")


@app.route('/allMovie', methods=['GET', 'POST'])
def movies():
    app.logger.info("The all movies page is requested")
    try:
        # Only login to view details
        userid = session.get('userid')
        if userid is None:
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(id=userid).first()
            is_active = user.is_active
            if is_active == 0:
                return redirect(url_for('logout'))
        role = session.get('role')
        if (role == 'admin'):
            return redirect(url_for('manageMovie'))

        genre_list = Genre.query.all()

        # Get the search keyword from the request
        search_query = request.args.get('search', '')

        # Gets the genre_id parameter passed in the front end
        genre_id = request.args.get('genre_id', "0")  # default is "0"(ALL)
        sort_order = request.args.get('sort_order', 'Null')  # default is Null

        page = request.args.get('page', 1, type=int)
        per_page = 9
        # display movie according to the genre
        if genre_id == "0":
            movie_query = Movie.query
        else:
            genre = Genre.query.filter_by(id=genre_id).first()
            movie_query = Movie.query.filter(
                Movie.id.in_([movie.id for movie in genre.belong_genre]))

        # Apply search filter if the search_query is not empty
        if search_query:
            movie_query = movie_query.filter(
                Movie.movie_title.ilike(f'%{search_query}%'))

        # Apply sorting based on the sort_order
        if sort_order == 'Ascend':
            movie_query = movie_query.order_by(Movie.average_rating.asc())
        elif sort_order == 'Descend':
            movie_query = movie_query.order_by(Movie.average_rating.desc())

        movie_list = movie_query.paginate(page=page, per_page=per_page,
                                          error_out=False)

        # get the number of movie
        movie_number = movie_query.count()

        return render_template(
            'allMovie.html',
            title='All Movies',
            movie_list=movie_list,
            movie_number=movie_number,
            genre_list=genre_list,
            search=search_query,
            genre_id=genre_id,
            sort_order=sort_order
        )
    except Exception as e:
        app.logger.error(f"An error appears when loading all movies page：{str(e)}")


@app.route('/detail/<int:movie_id>', methods=['GET', 'POST'])
def detail(movie_id):
    app.logger.info("The movie detail page is requested")
    try:
        # Only login to view details
        userid = session.get('userid')
        if userid is None:
            return redirect(url_for('login'))
        else:
            movie = Movie.query.filter_by(id=movie_id).first()

            user = User.query.filter_by(id=userid).first()

            is_active = user.is_active
            if is_active == 0:
                return redirect(url_for('logout'))
            role = session.get('role')
            if (role == 'admin'):
                return redirect(url_for('manageMovie'))

            # Determine whether the user is a favorite
            if movie in user.favorite_movies:
                is_favorite = True
            else:
                is_favorite = False

            # show reviews
            evaluates = Evaluate.query.filter_by(movie_id=movie_id).all()
            # write comment and mark
            form = EvaluateForm()
            if form.validate_on_submit():
                new_evaluate = Evaluate(
                    user_id=user.id,
                    movie_id=movie_id,
                    rating=form.rating.data,
                    comment=form.comment.data
                )
                db.session.add(new_evaluate)
                db.session.commit()
                log_user_action(userid,
                                'evaluate',
                                'Post the evaluate of movie {}.'.format(movie_id))
                return redirect(url_for('detail', movie_id=movie_id))
            return render_template('detail.html',
                                   title='View Detail',
                                   movie=movie,
                                   form=form,
                                   evaluates=evaluates,
                                   is_favorite=is_favorite)
    except Exception as e:
        app.logger.error(f"An error appears when loading the movie detail page：{str(e)}")


@app.route('/add_favorite', methods=['POST', 'GET'])
def add_favorite():
    user_id = request.form.get('user_id')
    movie_id = request.form.get('movie_id')
    user = User.query.get(user_id)
    movie = Movie.query.get(movie_id)
    user.favorite_movies.append(movie)
    db.session.commit()
    log_user_action(user_id,
                    'add_favorite',
                    'user add movie {} into favorite'.format(movie_id))
    return jsonify({"success": True})


@app.route('/remove_favorite', methods=['POST', 'GET'])
def remove_favorite():
    user_id = request.form.get('user_id')
    movie_id = request.form.get('movie_id')
    user = User.query.get(user_id)
    movie = Movie.query.get(movie_id)
    user.favorite_movies.remove(movie)
    db.session.commit()
    log_user_action(user_id,
                    'remove_favorite',
                    'user remove movie {} from favorite'.format(movie_id))
    return jsonify({"success": True})


@app.route('/myfavorite', methods=['GET', 'POST'])
def myfavorite():
    app.logger.info("The my favorites page is requested")
    try:
        # Only login and is active
        userid = session.get('userid')
        if userid is None:
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(id=userid).first()
            is_active = user.is_active
            if is_active == 0:
                return redirect(url_for('logout'))
        role = session.get('role')
        if (role == 'admin'):
            return redirect(url_for('manageMovie'))
        # the pagination
        page = request.args.get('page', 1, type=int)
        per_page = 6
        movie_list = Movie.query.join(user_movie_favorite).join(User).filter(
            User.id == user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # count the number of favorite movies
        movie_number = movie_list.total
        return render_template('myfavorite.html',
                               title='Favorite Movies',
                               movie_list=movie_list,
                               user=user,
                               movie_number=movie_number)
    except Exception as e:
        app.logger.error(f"An error appears when loading my favorite page：{str(e)}")


@app.route('/mycomment', methods=['GET', 'POST'])
def mycomment():
    app.logger.info("The my comment page is requested")
    try:
        # Only login and is active
        userid = session.get('userid')
        if userid is None:
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(id=userid).first()
            is_active = user.is_active
            if is_active == 0:
                return redirect(url_for('logout'))
            role = session.get('role')
            if (role == 'admin'):
                return redirect(url_for('manageMovie'))

        page = request.args.get('page', 1, type=int)
        per_page = 6
        evaluates = Evaluate.query.filter_by(user_id=user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        evaluates_number = evaluates.total
        return render_template('mycomment.html',
                               title='My Comment',
                               evaluates=evaluates,
                               evaluates_number=evaluates_number)
    except Exception as e:
        app.logger.error(f"An error appears when loading my comment page：{str(e)}")


# Recommend movies that the user might be interested in
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    app.logger.info("The recommended movies page is requested")
    try:
        userid = session.get('userid')

        if userid is not None:
            user = User.query.filter_by(id=userid).first()

            is_active = user.is_active
            if is_active == 0:
                return redirect(url_for('logout'))

            role = session.get('role')
            if (role == 'admin'):
                return redirect(url_for('manageMovie'))
        else:
            flash("Please log in to get personalized recommendations.")
            return redirect(url_for('login'))
        # Obtain the favorite records of the current user
        favorite_movies = user.favorite_movies
        favorite_movie_ids = [fav.id for fav in favorite_movies]

        # If no favorites, recommended by the average rating
        if not favorite_movie_ids:
            recommended_movies = Movie.query.order_by(
                Movie.average_rating.desc()).limit(5).all()
        else:
            # If has favorites, make recommendations based on movie similarity
            favorite_movies = Movie.query.filter(
                Movie.id.in_(favorite_movie_ids)).all()
            similarity_scores = {}
            # Iterate through all movies to calculate similarity
            all_movies = Movie.query.all()
            for movie in all_movies:
                if movie.id in favorite_movie_ids:
                    continue
                score = 0
                for fav_movie in favorite_movies:
                    score += similarity(fav_movie.id, movie.id)
                similarity_scores[movie] = score

            # recommend the top 5 movies
            recommended_movies = sorted(similarity_scores.keys(),
                                        key=lambda m: similarity_scores[m],
                                        reverse=True)[:5]

            log_user_action(userid, ''
                                    'view recommendation',
                            'get recommendation with movie '
                            'id {}'.format(recommended_movies))
        return render_template('recommend.html',
                               title='Recommended Movie',
                               recommended_movies=recommended_movies,)
    except Exception as e:
        app.logger.error(f"An error appears when loading the recommended movies page：{str(e)}")


# Calculate the similarity between two movies base on their overview
def similarity(movie_id1, movie_id2):
    overview1 = Movie.query.filter(Movie.id == movie_id1).first().overview
    overview2 = Movie.query.filter(Movie.id == movie_id2).first().overview
    movies_overviews = []
    movies_overviews.append(overview1)
    movies_overviews.append(overview2)

    # Use TfidfVectorizer to convert keywords into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(movies_overviews)

    # Calculate the cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix)
    return cosine_similarities[0][1]


@app.route('/manageMovie', methods=['GET', 'POST'])
def manageMovie():
    app.logger.info("The movie management page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    # Only is admin
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        genre_list = Genre.query.all()
        # Get the search keyword from the request
        search_query = request.args.get('search', '')

        # Gets the genre_id parameter passed in the front end
        genre_id = request.args.get('genre_id', "0")  # default is "0"(ALL)
        sort_order = request.args.get('sort_order', 'Null')  # default is Null

        page = request.args.get('page', 1, type=int)
        per_page = 10
        # display movie according to the genre
        if genre_id == "0":
            movie_query = Movie.query
        else:
            genre = Genre.query.filter_by(id=genre_id).first()
            movie_query = Movie.query.filter(
                Movie.id.in_([movie.id for movie in genre.belong_genre]))

        # Apply search filter if the search_query is not empty
        if search_query:
            movie_query = movie_query.filter(
                Movie.movie_title.ilike(f'%{search_query}%'))

        # Apply sorting based on the sort_order
        if sort_order == 'Ascend':
            movie_query = movie_query.order_by(Movie.average_rating.asc())
        elif sort_order == 'Descend':
            movie_query = movie_query.order_by(Movie.average_rating.desc())

        movie_list = movie_query.paginate(
            page=page, per_page=per_page, error_out=False)

        # get the number of movie
        movie_number = movie_query.count()
        return render_template('manageMovie.html',
                               title='Movie Management',
                               movie_list=movie_list,
                               genre_list=genre_list,
                               search=search_query,
                               genre_id=genre_id,
                               sort_order=sort_order,
                               movie_number=movie_number)
    except Exception as e:
        app.logger.error(f"An error appears when loading the movie management page：{str(e)}")


# Route for deleting a movie
@app.route('/delete', methods=['POST'])
def delete():
    user_id = session.get('userid')
    # Get JSON data from the request
    data = request.get_json()
    movie_id = data.get('movie_id')
    # Delete the movie and related infor from the database
    movie = Movie.query.filter_by(id=movie_id).first()
    evaluate_records = Evaluate.query.filter_by(movie_id=movie_id).all()
    for evaluate in evaluate_records:
        db.session.delete(evaluate)
    db.session.execute(user_movie_favorite.delete().where(
        user_movie_favorite.c.movie_id == movie_id))
    db.session.execute(movie_genre.delete().where(
        movie_genre.c.movie_id == movie_id))
    db.session.delete(movie)
    db.session.commit()

    log_user_action(user_id, 'Delete', "administrator deleted the movie")
    return redirect('')


# Route for editing an existing movie
@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    app.logger.info("The movie edit page is requested")
    try:
        user_id = session.get('userid')
        # Retrieve the movie by ID and pre-fill the form
        movie = Movie.query.filter_by(id=movie_id).first()
        form = CreateMovieForm(obj=movie)
        form.genres.data = [genre.name for genre in movie.genres]

        # Prepare movie data for comparison
        movie_data = {
            'movie_title': movie.movie_title,
            'release_date': movie.release_date,
            'runtime': movie.runtime,
            'overview': movie.overview,
            'tagline': movie.tagline,
            'backdrop_path': movie.backdrop_path,
            'poster_path': movie.poster_path,
            'spoken_languages': movie.spoken_languages,
            'director': movie.director,
            'average_rating': movie.average_rating,
            'certificate': movie.certificate,
            'star1': movie.star1,
            'star2': movie.star2
        }

        if form.validate_on_submit():
            selected_genres = set(request.form.getlist('genres'))

            # Check if no changes have been made
            if all(movie_data[key] == getattr(form, key).data
                   for key in movie_data) and \
               sorted(selected_genres) == sorted([genre.name
                                                  for genre in movie.genres]):
                flash('Update failure! No changes have been made.', 'error')
                return redirect(url_for('edit', movie_id=movie.id))

            # Check if a same movie already exists
            existing_movie = Movie.query.filter(
                Movie.id != movie_id,
                *[getattr(Movie, key) == getattr(form, key).data for
                  key in movie_data]
            ).first()

            if existing_movie and selected_genres == set(
                    [genre.name for genre in existing_movie.genres]):
                flash('Update failure! A same movie already exists.', 'error')
                return redirect(url_for('edit', movie_id=movie.id))

            # Update movie fields
            for key in movie_data:
                setattr(movie, key, getattr(form, key).data)

            # Update genres
            movie.genres.clear()
            for genre_name in selected_genres:
                genre = Genre.query.filter_by(name=genre_name).first()
                if genre:
                    movie.genres.append(genre)

            db.session.commit()
            log_user_action(user_id, 'Edit', "administrator edits the movie")
            flash('Updated successfully.', 'success')
            return redirect(url_for('edit', movie_id=movie_id))

        return render_template('editMovie.html',
                               title='Edit Assessment',
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the movie edit page：{str(e)}")


@app.route('/createMovie', methods=['GET', 'POST'])
def createMovie():
    app.logger.info("The movie create page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        user_id = session.get('userid')
        form = CreateMovieForm()
        if form.validate_on_submit():
            # ensure the movie is unique
            selected_genres = set(form.genres.data)
            existing_movie = Movie.query.filter(
                Movie.movie_title == form.movie_title.data,
                Movie.release_date == form.release_date.data,
                Movie.director == form.director.data,
                Movie.spoken_languages == form.spoken_languages.data,
                Movie.certificate == form.certificate.data,
                Movie.star1 == form.star1.data,
                Movie.star2 == form.star2.data,
                Movie.runtime == form.runtime.data,
                Movie.tagline == form.tagline.data,
                Movie.overview == form.overview.data,
                Movie.backdrop_path == form.backdrop_path.data,
                Movie.poster_path == form.poster_path.data,
                Movie.average_rating == form.average_rating.data
            ).first()

            if existing_movie:
                # Compare genres
                existing_genres = set(
                    [genre.name for genre in existing_movie.genres])
                if selected_genres == existing_genres:
                    flash('Create failure! A same movie already exists.', 'error')
                    return redirect(url_for('createMovie'))

            # Create and add new assessment if no duplicate exists
            new_movie = Movie(
                movie_title=form.movie_title.data,
                release_date=form.release_date.data,
                runtime=form.runtime.data,
                overview=form.overview.data,
                tagline=form.tagline.data,
                backdrop_path=form.backdrop_path.data,
                poster_path=form.poster_path.data,
                spoken_languages=form.spoken_languages.data,
                director=form.director.data,
                average_rating=form.average_rating.data,
                certificate=form.certificate.data,
                star1=form.star1.data,
                star2=form.star2.data
            )
            db.session.add(new_movie)
            db.session.commit()
            # Add selected genres to the movie
            selected_genres = form.genres.data
            for genre_name in selected_genres:
                genre = Genre.query.filter_by(name=genre_name).first()
                if genre:
                    new_movie.genres.append(genre)
            db.session.commit()
            log_user_action(user_id, 'Create', "administrator creates the movie")
            flash('Create successfully.', 'success')
            return redirect(url_for('createMovie'))

        return render_template('createMovie.html',
                               title='Add Movie',
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading create movie page：{str(e)}")


@app.route('/manageUser', methods=['GET', 'POST'])
def manageUser():
    app.logger.info("The user management page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        user_list = User.query.paginate(
            page=page, per_page=per_page, error_out=False)
        return render_template('manageUser.html',
                               title='User Management',
                               user_list=user_list)
    except Exception as e:
        app.logger.error(f"An error appears when loading user management page：{str(e)}")


# Route for editing an existing user
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    app.logger.info("The edit user page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        user = User.query.filter_by(id=user_id).first()
        form = ManageUserForm(obj=user)

        if form.validate_on_submit():
            movie_ids = re.findall(r'<Movie (\d+)>', form.favorite_movies.data)
            movie_ids_set_new = set(map(int, movie_ids))
            movie_ids_set_db = set([movie.id for movie in user.favorite_movies])
            # Check for changes
            if (user.avatar == form.avatar.data and
                user.username == form.username.data and
                user.role == form.role.data and
                user.is_active == int(form.is_active.data) and
                    movie_ids_set_db == movie_ids_set_new):
                flash('Update failure! No changes have been made.',
                      'error')
                return redirect(url_for('edit_user', user_id=user_id))

            # check that the username already exists
            if user.username != form.username.data:
                existing_user = User.query.filter_by(
                    username=form.username.data).first()
                if existing_user:
                    flash('Update failure! '
                          'Username already exists, please choose another one.',
                          'error')
                    return redirect(url_for('edit_user', user_id=user_id))

            # get user data
            user.avatar = form.avatar.data
            user.username = form.username.data
            user.role = form.role.data
            user.is_active = int(form.is_active.data)
            # Update the user's favorite movie list
            movies_to_remove = movie_ids_set_db - movie_ids_set_new
            for movie_id in movies_to_remove:
                movie = Movie.query.get(movie_id)
                if movie in user.favorite_movies:
                    user.favorite_movies.remove(movie)
            movies_to_add = movie_ids_set_new - movie_ids_set_db
            for movie_id in movies_to_add:
                movie = Movie.query.get(movie_id)
                if movie:
                    user.favorite_movies.append(movie)

            try:
                db.session.commit()
                flash('Updated successfully.', 'success')
                return redirect(url_for('edit_user', user_id=user_id))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'error')

        return render_template('editUser.html', title='Edit User', form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the edit user page：{str(e)}")


@app.route('/manageGenre', methods=['GET', 'POST'])
def manageGenre():
    app.logger.info("The genre management page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        genre_list = Genre.query.paginate(
            page=page, per_page=per_page, error_out=False)
        return render_template('manageGenre.html',
                               title='Genre Management',
                               genre_list=genre_list)
    except Exception as e:
        app.logger.error(f"An error appears when loading the genre management page：{str(e)}")


@app.route('/create_genre', methods=['GET', 'POST'])
def create_genre():
    app.logger.info("The genre create page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        user_id = session.get('userid')
        form = ManageGenreForm()
        if form.validate_on_submit():
            # ensure the genre is unique
            existing_genre = Genre.query.filter(
                Genre.name == form.name.data
            ).first()

            if existing_genre:
                flash('Create failure! A same genre already exists.', 'error')
                return redirect(url_for('create_genre'))

            # Create and add new genre if no duplicate exists
            new_genre = Genre(name=form.name.data)
            db.session.add(new_genre)
            db.session.commit()
            log_user_action(user_id, 'Create', "administrator creates the genre")
            flash('Create successfully.', 'success')
            return redirect(url_for('create_genre'))

        return render_template('createGenre.html',
                               title='Create Genre',
                               form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the create genre page：{str(e)}")


@app.route('/edit_genre/<int:genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    app.logger.info("The genre edit page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        user_id = session.get('userid')

        genre = Genre.query.filter_by(id=genre_id).first()
        form = ManageGenreForm(obj=genre)

        if form.validate_on_submit():
            # check whether edit
            if (genre.name == form.name.data):
                flash('Update failure! No changes have been made.', 'error')
                return redirect(url_for('edit_genre', genre_id=genre_id))

            # If edit, check to see if it already exists
            if genre.name != form.name.data:
                existing_genre = Genre.query.filter_by(name=form.name.data).first()
                if existing_genre:
                    flash('Update failure! '
                          'Genre already exists, please choose another one.',
                          'error')
                    return redirect(url_for('edit_genre', genre_id=genre_id))

            # update data
            genre.name = form.name.data
            db.session.commit()
            flash('Updated successfully.', 'success')
            log_user_action(user_id, 'edit genre',
                            "administrator edits the genre.")
            return redirect(url_for('edit_genre', genre_id=genre_id))
        return render_template('editGenre.html', title='Edit Genre', form=form)
    except Exception as e:
        app.logger.error(f"An error appears when loading the edit genre page：{str(e)}")


@app.route('/delete_genre', methods=['POST'])
def delete_genre():
    user_id = session.get('userid')
    # Get JSON data from the request
    data = request.get_json()
    genre_id = data.get('genre_id')
    genre = Genre.query.filter_by(id=genre_id).first()
    db.session.delete(genre)
    db.session.commit()
    log_user_action(user_id, 'Delete', "administrator deleted the genre")
    return redirect('')


@app.route('/manage_comment', methods=['GET', 'POST'])
def manage_comment():
    app.logger.info("The comment management page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        comment_list = Evaluate.query.paginate(
            page=page, per_page=per_page, error_out=False)
        return render_template('manageComment.html',
                               title='Comment Management',
                               comment_list=comment_list)
    except Exception as e:
        app.logger.error(f"An error appears when loading the comment management page：{str(e)}")


@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    user_id = session.get('userid')
    # Get JSON data from the request
    data = request.get_json()
    comment_id = data.get('comment_id')
    comment = Evaluate.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    log_user_action(user_id, 'Delete', "deleted the comment")
    return redirect('')


@app.route('/userLog', methods=['GET', 'POST'])
def userLog():
    app.logger.info("The veiwing user log page is requested")
    # Only login
    userid = session.get('userid')
    if userid is None:
        return redirect(url_for('login'))
    role = session.get('role')
    if (role == 'user'):
        return redirect(url_for('index'))
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        log_list = UserLog.query.paginate(page=page, per_page=per_page,
                                          error_out=False)
        return render_template('userLog.html',
                               title='View User Log',
                               log_list=log_list)
    except Exception as e:
        app.logger.error(f"An error appears when loading the view user log page：{str(e)}")
