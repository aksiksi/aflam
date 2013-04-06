import random
import string
from flask import Flask, render_template, redirect, request, flash, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask.ext.bcrypt import Bcrypt
from datetime import date, timedelta
from forms import Signup, Login
from flask.ext.mail import Mail, Message

app = Flask(__name__)
app.config.from_object('config')

# Database setup
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '<span style="color: black;">Please login to access this page.</span>'

# Hashing setup
bcrypt = Bcrypt(app)

# Mail setup
mail = Mail(app)


@login_manager.user_loader
def load_user(userid):
    """Required by Flask-Login."""
    return models.User.query.filter_by(id=int(userid)).first()


@app.template_filter('dateformat')
def dateformat(value, format='%d-%m-%Y'):
    """Format dates in templates."""
    return date.strftime(value, format)


def send_validation_email(email):
    """Send an email to user for validation."""
    # Generate 30 character validation token with expiry date
    validation_token = ''.join([random.choice(string.letters + string.digits) for _ in range(30)])
    expires_on = date.today() + timedelta(days=3)

    # Setup message
    msg = Message(subject='[UAE Movies] Validate your account', recipients=[email], sender='verify@uaemovies.net')
    msg.html = '''Thank you for creating an account with UAE Movies! To verify your account, please follow the link
                  provided below.\n\n <insert url here>%s''' % validation_token

    return validation_token

@app.route('/')
def index():
    """Homepage."""
    now_showing = []
    coming_soon = []

    movies = models.Movie.query.all()

    for movie in movies:
        if movie.released:
            now_showing.append(movie)
        else:
            coming_soon.append(movie)

    return render_template('index.html', now_showing=sorted(now_showing)[:6], coming_soon=sorted(coming_soon)[:6])


@app.route('/now')
def now_showing():
    """Now showing page."""
    movies = models.Movie.query.filter_by(now_showing=True)
    return render_template('now_showing.html', movies=sorted(movies))


@app.route('/soon')
def coming_soon():
    """Coming soon page."""
    movies = models.Movie.query.filter_by(released=False)
    return render_template('coming_soon.html', movies=sorted(movies))


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

#TODO: Finish up remaining views

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in a verified user."""
    if current_user.is_anonymous():
        form = Login()
        if form.validate_on_submit():
            user = models.User.query.filter_by(username=form.username.data).first()
            if user and user.check_pw(form.password.data):
                if user.is_authenticated():
                    login_user(user, remember=form.remember.data)
                    flash('Logged in successfully!', 'success')
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    flash('Your account is either not verified or disabled.', 'failure')
            else:
                flash('Username or password is incorrect.', 'failure')
        return render_template('login.html', form=form)
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Creates a user if current user is anonymous."""
    if current_user.is_anonymous():
        form = Signup()
        if form.validate_on_submit():
            # validation_token, expires_on = send_validation_email(form.email.data)

            email_obj = models.User.query.filter_by(email=form.email.data).first()
            username_obj = models.User.query.filter_by(username=form.username.data).first()

            # Run checks to make sure username and email are not already taken
            if username_obj and email_obj:
                form.username.errors.append('Username is already taken.')
                form.email.errors.append('Email is already taken.')
            elif username_obj:
                form.username.errors.append('Username is already taken.')
            elif email_obj:
                form.email.errors.append('Email is already taken.')
            else:
                u = models.User(username=form.username.data, password=form.password.data, email=form.email.data,
                                first_name=form.first_name.data, last_name=form.last_name.data, gender=form.gender.data,
                                validation_token='test123')

                db.session.merge(u)
                db.session.commit()

                flash('Sign up successful! Please check your email for a validation link.', 'success')

                return redirect(url_for('index'))
        return render_template('signup.html', form=form)

    return redirect(url_for('index'))


@app.route('/verify')
def verify():
    """Verifies a registered user if not already verified."""
    email, validation_token = request.args.get('e'), request.args.get('t')

    user = models.User.query.filter_by(email=email).first()

    if user:
        if not user.verified:
            if user.validation_token == validation_token:
                user.verified = True
                db.session.merge(user)
                db.session.commit()
                flash('Your account is now verified!', 'success')
            else:
                flash('Sorry, but the verification URL is incorrect. Please try again or <a href="#">request</a> \
                       a new link.', 'failure')
        else:
            flash('Your account is already verified.', 'failure')
    else:
        flash('Sorry, but the verification URL is incorrect. Please try again or <a href="#">request</a> a new link.',
              'failure')

    return redirect(url_for('index'))


@app.route('/resend')
def resend():
    """Resends validation email to user."""
    # TODO: Implement secure form for resend
    email = request.args.get('e')
    user = models.User.query.filter_by(email=email).first()

    if user:
        user.validation_token = send_validation_email(email)
        user.validation_expiry = date.today() + timedelta(days=3)
        db.session.merge(user)
        db.session.commit()
        flash('Verification email resent successfully.', 'success')
    else:
        flash('User with this email does not exist.', 'failure')

    return redirect(url_for('index'))

@app.route('/recover')
def recover():
    """Sends new, random password to user's email."""
    pass

@app.route('/logout')
def logout():
    if current_user.is_active():
        logout_user()
        flash('Successfully logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


@app.route('/settings')
@login_required
def settings():
    pass


@app.route('/profile/<username>')
def show_profile(username):
    pass

# Error handlers
@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

import models

if __name__ == '__main__':
    app.run(host='0.0.0.0')
