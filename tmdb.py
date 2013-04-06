__author__ = 'Assil Ksiksi'

import requests
from datetime import date, datetime

_API_KEY = ""
_DEFAULT_IMAGE = "http://i.imgur.com/Ub67KNH.png"


def set_api_key(api_key):
    """Set your TMDB API key."""
    global _API_KEY
    _API_KEY = api_key


def set_default_image(image_url):
    """Provide the image URL to use as a poster fallback."""
    global _DEFAULT_IMAGE
    _DEFAULT_IMAGE = image_url


class MovieBase(object):
    """Base class for Movie. Used to represent movies that are not on TMDB."""
    def __init__(self, movie_title, release_date=date.today()):
        self.release_date = release_date
        self.movie_title = movie_title

    def local_release_date(self):
        """Return movie's local release date (provided as input) -- date."""
        return self.release_date

    def global_release_date(self):
        """Return movie's global release date -- date."""
        return self.release_date

    def overview(self):
        """Return brief overview of movie's plot -- string."""
        return "Not available."

    def runtime(self):
        """Return movie's runtime in minutes -- integer."""
        return 0

    def tmdb_id(self):
        """Return movie's TMDB ID -- integer."""
        return 0

    def imdb_url(self):
        """Return movie's IMDB URL -- string."""
        return ""

    def old_title(self):
        """Return movie's old title -- string."""
        return self.movie_title

    def title(self):
        """Return movie's title -- string."""
        return self.movie_title

    def poster_url(self):
        """Return a URL to the movie's poster -- string."""
        return _DEFAULT_IMAGE

    def __str__(self):
        return "<Movie (%s - %d)>" % (self.title(), self.global_release_date().year)


class Movie(MovieBase):
    """Create an object containing movie info of passed title acquired using themoviedb.org API."""
    def __init__(self, movie_title, release_date=date.today()):
        super(MovieBase, self).__init__()
        self.release_date = release_date
        self.movie_title = movie_title
        self.id = self._get_movie_id(self.movie_title, _API_KEY, release_date.year)

        if not self.id:  # Raise an exception if movie cannot be found using API
            raise ValueError("ID is invalid.")

        self.movie_info = requests.get("http://api.themoviedb.org/3/movie/{0}?api_key={1}"
                                       .format(self.id, _API_KEY)).json()

    def global_release_date(self):
        """Return movie's global release date -- date."""
        global_release_date = self.movie_info["release_date"]
        if global_release_date:
            return datetime.strptime(global_release_date, "%Y-%m-%d")
        else:
            return self.release_date

    def overview(self):
        """Return brief overview of movie's plot -- string."""
        return self.movie_info["overview"]

    def runtime(self):
        """Return movie's runtime in minutes -- integer."""
        return self.movie_info["runtime"]

    def tmdb_id(self):
        """Return movie's TMDB ID -- integer."""
        return self.id

    def imdb_url(self):
        """Return movie's IMDB URL -- string."""
        imdb_id = self.movie_info["imdb_id"]
        if imdb_id:
            return "http://imdb.com/title/" + self.movie_info["imdb_id"]
        else:
            return ""

    def poster_url(self):
        """Return sub-path of movie's poster or entire URL of fallback image -- string."""
        poster_path = self.movie_info["poster_path"]
        if poster_path:
            return self.movie_info["poster_path"]
        else:
            return _DEFAULT_IMAGE

    def title(self):
        """Return movie's title -- string."""
        return self.movie_info["title"]

    def _get_movie_id(self, title, api_key, release_year):
        """Finds TMDB ID of given title and year. Checks 2 years before in case given year is incorrect."""
        min_year = release_year - 2

        # Iterate through past years, starting from release_year
        for year in reversed(range(min_year, release_year + 1)):
            search_results = requests.get("http://api.themoviedb.org/3/search/movie?api_key={0}&query={1}&year={2}"
                                          .format(api_key, title, year)).json()

            try:
                movie_id = search_results["results"][0]["id"]  # Try getting the id of the first result
            except IndexError:
                movie_id = None

            if movie_id:
                return movie_id

        # As a fallback, return None
        return None