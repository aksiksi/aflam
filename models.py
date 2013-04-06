__author__ = 'Cyph0n'

from views import db, bcrypt
from datetime import datetime, date
from flask.ext.login import UserMixin


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    old_title = db.Column(db.String)
    local_release_date = db.Column(db.Date)
    global_release_date = db.Column(db.Date)
    imdb_url = db.Column(db.String)
    tmdb_id = db.Column(db.String)
    poster_url = db.Column(db.String)
    runtime = db.Column(db.Integer)
    overview = db.Column(db.String)
    released = db.Column(db.Boolean)
    now_showing = db.Column(db.Boolean)
    added_on = db.Column(db.DateTime)
    last_modified = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, title, old_title, local_release_date, global_release_date, imdb_url, tmdb_id, poster_url,
                 runtime, overview, now_showing=False, released=False):
        self.title = title
        self.old_title = old_title
        self.local_release_date = local_release_date
        self.global_release_date = global_release_date
        self.imdb_url = imdb_url
        self.tmdb_id = tmdb_id
        self.poster_url = poster_url
        self.runtime = runtime
        self.overview = overview
        self.released = released
        self.now_showing = now_showing
        self.added_on = datetime.now()  # Add this on creation

    def __lt__(self, other):
        return self.local_release_date < other.local_release_date

    def __repr__(self):
        return "<Movie (%s, %s, released=%s, showing=%s)>" % (self.title, self.tmdb_id, self.released, self.now_showing)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    _password = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    full_name = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    gender = db.Column(db.String(10))
    verified = db.Column(db.Boolean)
    validation_token = db.Column(db.String)
    validation_expiry = db.Column(db.Date)
    suspended = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime)
    profile_public = db.Column(db.Boolean)
    watched_movies = db.Column(db.PickleType())  # comparator=lambda obj, needed: all([val in obj for val in needed])))
    last_login = db.Column(db.DateTime)

    def __init__(self, username, password, email, first_name, last_name, gender, validation_token,
                 validation_expiry=date.today(), suspended=False, verified=False, profile_public=True):
        self.username = username
        self._password = bcrypt.generate_password_hash(password)
        self.email = email
        self.full_name = first_name + " " + last_name
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.validation_token = validation_token
        self.suspended = suspended
        self.verified = verified
        self.created_on = datetime.now()
        self.profile_public = profile_public

    # Password manipulation methods
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pw):
        self._password = bcrypt.generate_password_hash(pw)

    def check_pw(self, pw):
        return bcrypt.check_password_hash(self._password, pw)

    # For Flask-Login
    def is_authenticated(self):
        return self.verified and not self.suspended


