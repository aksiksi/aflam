import unittest
import tmdb
from models import Movie
from datetime import date
from views import app, db
from flask.ext.testing import TestCase
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask


class TmdbTest(unittest.TestCase):
    def setUp(self):
        self.movie = tmdb.Movie(movie_title="Shame", release_date=date.today())

    def test_release_date(self):
        self.assertEquals(self.movie.global_release_date().year, 2011)

    def test_imdb_url(self):
        self.assertEquals(self.movie.imdb_url(), "http://imdb.com/title/tt1723811")

    def test_str(self):
        self.assertEquals(str(self.movie), "<Movie (%s - %d)>" % (self.movie.title(), self.movie.global_release_date().year))


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        # Set app up for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True

        self.db = db
        self.db.create_all()

        self.m = Movie(title="Shame", old_title="SHAME", local_release_date=date.today(), global_release_date=date
                       .today(), imdb_url="abcd", tmdb_id="efgh", poster_url="http://", runtime=109, overview="abcdefg")

        self.db.session.add(self.m)
        self.db.session.commit()

    def test_retrieve_movie(self):
        m = Movie.query.first()
        self.assertEquals(m.runtime, self.m.runtime)
        self.assertEquals(m.title, self.m.title)

    def test_modify_movie(self):
        m = Movie.query.first()
        m.runtime = 102
        m.title = "Baloney"

        self.db.session.add(m)
        self.db.session.commit()

        m = Movie.query.first()
        self.assertEquals(m.runtime, 102)
        self.assertEquals(m.title, "Baloney")

    def test_remove_movie(self):
        m = Movie.query.first()

        self.db.session.delete(m)
        self.db.session.commit()

        self.assertEquals(Movie.query.first(), None)

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

# TODO: Add views tests

if __name__ == '__main__':
    unittest.main()