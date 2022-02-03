import requests


class Imdb:
    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def _base_imdb_request(path: str):
        response = requests.get(
            url=f"https://imdb-api.com/API/{path}",
        )
        return response

    def movie_ratings(self, movie_id: str):
        response = self._base_imdb_request(f"Ratings/{self.api_key}/{movie_id}")
        if response.status_code != 200:
            raise Exception(
                f"Something went wrong searching for the ratings of the movie {movie_id}"
            )
        return response.json()
