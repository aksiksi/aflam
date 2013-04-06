# Overview

## What?

A cinema release tracker for the UAE written in Python using the [Flask](http://flask.pocoo.org/) microframework. The application is **not** complete, but it does have a functioning auth system implemented using a variety of plugins, including:

* [Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/)
* [Flask-WTF](http://pythonhosted.org/Flask-WTF/)
* [Flask-Login](http://pythonhosted.org/Flask-Login/)
* [Flask-Mail](http://packages.python.org/flask-mail/)
* [Flask-Bcrypt](http://pythonhosted.org/Flask-Bcrypt/)

It also depends on the following libraries for certain other functions:

* [Requests](http://docs.python-requests.org/en/latest/index.html)
* [lxml](http://lxml.de)
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)

`lxml` is optional, but preffered. If you do not want to use it, open `grab.py` and simply remove it as a second parameter to the two `BeautifulSoup` objects.

    soup = BeautifulSoup(..., "lxml") # Remove "lxml" (and the comma, of course)

## Why?

It was supposed to become a large-scale movie release tracker for the UAE, but was unfortunately an over-ambitious project from the get-go.

## How?

**aflam** scrapes movie release info from the [Vox Cinemas](http://voxcinemas.com) homepage, then processes it using **themoviedb.org**'s API. The resulting data is stored into a database table using the [SQLAlchemy ORM](http://www.sqlalchemy.org/). The final piece, the website, uses this stored data in its views and adds user accounts and authentication to the mix.

# Setup

To run the application, you'll obviously need to install Flask and the extensions mentioned above. This can be done in one step using the included `requirements.txt`.

    pip install -r "requirements.txt"

You'll then need to modify a few settings.

1. In `config.py`, set `SQLALCHEMY_DATABASE_URI` to your database's link.
2. In `tmdb.py`, set `API_KEY` to your tMDB API key. Obviously, you'll need to apply for one. You can read more about it [here](http://www.themoviedb.org/documentation/api).

With the above done, the web app should run (almost) perfectly.

# Bugs and Issues

If you ever run this application and find a bug or two, don't hesitate to report it using the Issue Tracker.