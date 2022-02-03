import requests


class Tmdb:
    api_key: str
    language: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.language = "language=en-US"

    @staticmethod
    def _base_tmdb_request(path: str):
        response = requests.get(
            url=f"https://api.themoviedb.org/3/{path}",
        )

        return response

    def search_movie(self, expression: str):
        response = self._base_tmdb_request(
            f"search/movie?{self.api_key}&{self.language}&query={expression}&page=1"
        )
        if response.status_code != 200:
            raise Exception(f"Something went wrong searching the movie {expression}")
        return response.json()

    def movie_credits(self, movie_id):
        response = self._base_tmdb_request(
            f"movie/{movie_id}/credits?{self.api_key}&{self.language}"
        )
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong searching the credits of movie {movie_id}"
            )
        return response.json()

    def movie_details(self, movie_id):
        response = self._base_tmdb_request(
            f"movie/{movie_id}?{self.api_key}&{self.language}"
        )
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong searching the details of movie {movie_id}"
            )
        return response.json()

    def popular_movies(self, page: int):
        response = self._base_tmdb_request(
            f"movie/popular?{self.api_key}&{self.language}&page={page}"
        )
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong retrieving Popular Movies, page {page}"
            )
        return response.json()

    def search_people(self, expression: str):
        response = self._base_tmdb_request(
            f"search/person?{self.api_key}&{self.language}&page=1&query={expression}"
        )
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong retrieving the name of the actor {expression}"
            )
        return response.json()

    def person_details(self, id_: str):
        response = self._base_tmdb_request(f"person/{id_}?{self.api_key}")
        if response.status_code != 200:
            raise Exception(f"Something went wrong retrieving the actor with id: {id_}")
        return response.json()

    def person_movie_credits(self, id_: str):
        response = self._base_tmdb_request(f"person/{id_}/movie_credits?{self.api_key}")
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong retrieving the person info with id: {id_}"
            )
        return response.json()

    def external_id(self, id_: str):
        response = self._base_tmdb_request(f"movie/{id_}/external_ids?{self.api_key}")
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong retrieving the external id of movie {id_}"
            )
        return response.json()
