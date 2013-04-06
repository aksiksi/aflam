import requests
import tmdb
from bs4 import BeautifulSoup
from datetime import datetime
from views import db
from models import Movie

headers = {"User-Agent": '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.31 (KHTML, like Gecko)
                            Chrome/26.0.1410.43 Safari/537.31'''}


def now_showing():
    """Returns dict of movie:date of movies that are now showing from VOX Cinemas website."""

    def strip_rating(title):
        """Removes trailing rating from movie title. Input must be list."""
        index = len(title) - 1
        if "(" in title:  # Make sure title has rating
            for char in reversed(title):
                title.pop(index)
                if char == "(":
                    break
                index -= 1
        return "".join(title).rstrip()

    soup = BeautifulSoup(requests.get("http://voxcinemas.com/", headers=headers).text, "lxml")
    selection = soup.select("div.now-showingin div.now-showing-movie")
    movies = {}

    for movie in selection:
        title = movie.select(".now-showing-movie-txt > a")[0].text
        stripped_title = strip_rating(list(title))  # Remove rating from end of title ex: Shame (PG13)
        movies[stripped_title] = datetime.now().date()

    return clean_up_titles(movies)


def coming_soon():
    """Returns dict of movie:date of movies that are coming soon from VOX Cinemas website."""
    soup = BeautifulSoup(requests.get("http://voxcinemas.com/coming-soon.aspx", headers=headers).text, "lxml")
    selection = soup.select("#ContentPlaceHolder1_ulComingSoon > li")
    movies = {}

    for movie in selection:
        info = [e.text for e in movie.select("a > b")]
        title, date_string = info[0], info[1]
        date = datetime.strptime(date_string, "(%d-%m-%Y)").date()
        movies[title] = date

    return clean_up_titles(movies)


def clean_up_titles(movies):
    """Cleans up messy titles by removing bad strings defined below."""
    bad_strings = [" 2D", "3D ", " - Hindi", " - Malayalam", " - Tagalog"]

    def remove_bad_strings(title, bad_strings):
        """Recursively removes bad strings from title."""
        if len(bad_strings) == 0:
            return title
        else:
            return remove_bad_strings(title.replace(bad_strings[0], ""), bad_strings[1:])

    # Remove junk from selected titles
    for title, release_date in movies.items():
        if any([s in title for s in bad_strings]):
            clean_title = remove_bad_strings(title, bad_strings)
            movies[clean_title] = release_date
            del movies[title]

    # Remove duplicates -- edge case, but as precaution
    to_remove = []
    for title in movies:
        if [key.lower() for key in movies].count(title.lower()) > 1:  # If a copy of the title exists in the movies dict
            if title.lower() not in [e.lower() for e in to_remove]:  # Make sure not already flagged for removal
                to_remove.append(title)

    for key in to_remove:
        del movies[key]

    return movies


def create_movie_objects(movies):
    """Takes a movie dict (title:date) as input and returns a list of Movie (or MovieBase) objects."""
    movie_objects = []

    for title, release_date in movies.items():
        try:
            movie_object = tmdb.Movie(movie_title=title, release_date=release_date)
        except IndexError:  # In case movie does not exist on TMDB, create a MovieBase object
            movie_object = tmdb.MovieBase(movie_title=title, release_date=release_date)
        finally:
            movie_objects.append(movie_object)

        print "    * {0} has been created.".format(title)

    return movie_objects


def store_now_showing():
    """Saves (or updates) movies that are now showing to the database."""
    now_showing_movies = now_showing()
    q = Movie.query.all()

    # Filter out movies that are already in database and update needed columns
    if q:
        for movie in q:
            if movie.old_title in now_showing_movies:
                if not movie.released:
                    movie.local_release_date = now_showing_movies[movie.old_title]  # Modify release date
                    movie.released, movie.now_showing = True, True
                del now_showing_movies[movie.old_title]
            else:
                if movie.now_showing:
                    movie.now_showing = False
            db.session.add(movie)

    now_showing_objects = create_movie_objects(now_showing_movies)

    # Process the remaining movies i.e. ones not already in DB
    for obj in now_showing_objects:
        m = Movie(obj.title(), obj.old_title(), obj.local_release_date(), obj.global_release_date(),
                  obj.imdb_url(), obj.tmdb_id(), obj.poster_url(), obj.runtime(), obj.overview(), True, True)
        db.session.add(m)

    db.session.commit()
    db.session.remove()

    return "Now showing movies successfully stored."


def store_coming_soon():
    """Saves (or updates) movies that are coming soon to the database."""
    coming_soon_movies = coming_soon()
    q = Movie.query.all()

    # Filter out movies that are already in database
    if q:
        for movie in q:
            if movie.old_title in coming_soon_movies:
                if not movie.released:
                    # If release date has been changed, update it
                    if movie.local_release_date != coming_soon_movies[movie.old_title]:
                        movie.local_release_date = coming_soon_movies[movie.old_title]
                        db.session.add(movie)
                del coming_soon_movies[movie.old_title]

    coming_soon_objects = create_movie_objects(coming_soon_movies)

    for obj in coming_soon_objects:
        m = Movie(obj.title(), obj.old_title(), obj.local_release_date(), obj.global_release_date(),
                  obj.imdb_url(), obj.tmdb_id(), obj.poster_url(), obj.runtime(), obj.overview())
        db.session.add(m)

    db.session.commit()
    db.session.remove()

    return "Coming soon movies successfully stored."


def main():
    print "Now showing..."
    print store_now_showing()
    print "Coming soon.."
    print store_coming_soon()

if __name__ == "__main__":
    main()
