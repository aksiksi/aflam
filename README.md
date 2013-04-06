# Overview

## What?

A cinema release tracker for the UAE written in Python using the Flask microframework. The application is **not** complete, but it does have a functioning auth system implemented using a variety of plugins, including:

* Flask-SQLAlchemy
* Flask-WTF
* Flask-Login
* Flask-Mail
* Flask-Bcrypt

## Why?

It was supposed to become a large-scale release tracker for the UAE, but it was an over-ambitious project from the get-go.

## How?

*aflam* scrapes movie release info from the Vox Cinemas homepage, then processes it using **themoviedb.org**'s API. The resulting data is stored into a database table using the SQLAlchemy ORM. The final piece, the website, uses this stored data in its views and adds user accounts to the mix.

# Setup

To run the application, you'll obviously need to install Flask and the extensions mentioned above. You'll also need to modify a few settings.

1) In `config.py`, set SQLALCHEMY_DATABASE_URI to your database's link.
2) In `tmdb.py`, set the API_KEY to your tMDB key. Obviously, you'll need to apply for one.

With the above done, the web app should run perfectly.

# Bugs and Issues

If you ever run this application and find a bug or two, don't hesitate to report it using the Issue Tracker.

