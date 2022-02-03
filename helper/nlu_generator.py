import random
from string import punctuation

from helper.dynamic_nlu_templates import INTENTS_TEMPLATE
from env import TMDB_APIKEY
from justwatch import JustWatch

from helper.tmdb import Tmdb

random.seed(10)
path_to_file = "../data/nlu.yml"

out = open(path_to_file, "w")
static_nlu = open("static_nlu.txt", "r")

out.write("nlu: \n")
# print the providers offering subscription options
just_watch = JustWatch(country="IT")
providers_monetization = {
    p["clear_name"]
    for p in just_watch.get_providers()
    if "flatrate" in p["monetization_types"]
}

for line in static_nlu:
    out.write(line)

out.write("\n\n")

tmdb = Tmdb(TMDB_APIKEY)
movies = [
    item["title"].rstrip(punctuation)
    for i in range(1, 51)
    for item in tmdb.popular_movies(i)["results"]
    if not item["adult"]
]

people = [
    person["name"].rstrip(punctuation)
    for item in tmdb.popular_movies(1)["results"]
    for person in tmdb.movie_credits(item["id"])["cast"]
]

for intent, sentences in INTENTS_TEMPLATE.items():
    out.write(f"- intent: {intent}\n")
    out.write("  examples: |\n")

    for question in sentences:
        for i in range(20):
            if intent in {
                "movie_provider",
                "all_stars_movie",
                "movie_director",
                "movie_writer",
                "movie_plot",
                "movie_reviews",
            }:
                q = question.format(movie=random.choice(movies))
                out.write(f"    - {q}\n")
                out.write(f"    - {q.lower()}\n")
        for i in range(50):
            if intent in {"person_info"}:
                q = question.format(person=random.choice(people))
                out.write(f"    - {q}\n")
                out.write(f"    - {q.lower()}\n")
    out.write("\n")
