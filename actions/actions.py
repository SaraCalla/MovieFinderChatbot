import string
from datetime import datetime
from statistics import mean

from typing import Dict, Text, Any, List, Set

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

from justwatch import JustWatch

from env import TMDB_APIKEY, IMDB_APIKEY
from helper.tmdb import Tmdb
from helper.imdb import Imdb


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

ERROR_MESSAGE = "Ops! This is embarrassing... Something went wrong. Please ask me your question again."


def get_printable_list(items: List[str]) -> str:
    return ", and ".join(
        [", ".join(items[:-1]), items[-1]] if len(items) > 2 else items
    )


def get_printable_set(items: Set[str]) -> str:
    return get_printable_list(list(items))


# class ActionUserProvider(Action):
#     def name(self) -> Text:
#         return "action_user_providers"
#
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#
#         print("I'm in action_user_providers")
#
#         providers_raw = set(tracker.get_latest_entity_values("provider"))
#         print(f"Sono in providers: {providers_raw}")
#
#         if providers_raw is not None:
#             print(f"Providers: {providers_raw}")
#             botResponse = f"Thanks! So your providers are: {get_printable_set(providers_raw)}. Right?"
#
#         else:
#             botResponse = ERROR_MESSAGE
#         dispatcher.utter_message(text=botResponse)
#
#         return []


class ActionAffirm(Action):
    def name(self) -> Text:
        return "action_affirm"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        events = []
        try:
            print("I'm in action_affirm")
            last_question = tracker.get_slot("last_question")

            if last_question == "movie_provider":
                res = "action_movie_provider"
                events.append(FollowupAction(res))
            elif last_question == "all_stars_movie":
                res = "action_all_stars_movie"
                events.append(FollowupAction(res))
            elif last_question == "movie_plot":
                res = "action_movie_plot"
                events.append(FollowupAction(res))
            elif last_question == "movie_reviews":
                res = "action_movie_reviews"
                events.append(FollowupAction(res))
            elif last_question == "movie_director":
                res = "action_movie_director"
                events.append(FollowupAction(res))
            elif last_question == "movie_writer":
                res = "action_movie_writer"
                events.append(FollowupAction(res))
            else:
                botResponse = (
                    "Mmm.. Sorry I couldn't understand your question. Can you repeat?"
                )
                dispatcher.utter_message(text=botResponse)
        except Exception as ex:
            botResponse = ERROR_MESSAGE
            dispatcher.utter_message(text=botResponse)

        return events


class ActionDeny(Action):
    def name(self) -> Text:
        return "action_deny"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("I'm in action_deny")
        botResponse = "What else can I do for you?"
        dispatcher.utter_message(text=botResponse)

        return [SlotSet("last_question", ""), SlotSet("movie", "")]


class ActionMovieProviders(Action):
    def name(self) -> Text:
        return "action_movie_provider"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        events = []

        print("I'm in action_movie_provider")

        movie_slot = tracker.get_slot("movie")

        just_watch = JustWatch(country="IT")
        providers_map = {p["id"]: p["clear_name"] for p in just_watch.get_providers()}

        movie_name = movie_slot
        movie_raw = next(tracker.get_latest_entity_values("movie"), None)
        if movie_name is None and movie_raw is not None:
            movie_name = string.capwords(movie_raw)

        print(f"Movie name: {movie_name}")
        if movie_name:
            result = just_watch.search_for_item(query=movie_name)["items"][0]
            movie_name = result["title"]
            flatrate_movie_providers = {
                providers_map[offer["provider_id"]]
                for offer in result.get("offers", [])
                if offer["monetization_type"] == "flatrate"
            }
            rent_movie_providers = {
                providers_map[offer["provider_id"]]
                for offer in result.get("offers", [])
                if offer["monetization_type"] == "rent"
            }
            if flatrate_movie_providers or rent_movie_providers:
                if flatrate_movie_providers and rent_movie_providers:
                    botResponse = f"Let me check... You can watch {movie_name} for free if you are subscribed on {get_printable_set(flatrate_movie_providers)}. Or you can rent it on {get_printable_set(rent_movie_providers)}"
                elif flatrate_movie_providers and rent_movie_providers is None:
                    botResponse = f"Let me check... You can watch {movie_name} for free if you are subscribed on {get_printable_set(flatrate_movie_providers)}."
                elif rent_movie_providers and flatrate_movie_providers is None:
                    botResponse = f"Let me check... You can watch {movie_name} by renting it on {get_printable_set(rent_movie_providers)}"
                else:
                    botResponse = f"Oh! I couldn't find any provider for {movie_name}."
            else:
                botResponse = f"Oh! I couldn't find any provider for {movie_name}."
            botResponse += f"\nWould you like to know who starred in {movie_name}?"
            events += [
                SlotSet("last_question", "all_stars_movie"),
                SlotSet("movie", movie_name),
            ]
            print(f"events in action_movie_provider: {events}")
        else:
            botResponse = ERROR_MESSAGE
            print(f"Movie name: {movie_name}")
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        dispatcher.utter_message(text=botResponse)

        return events


class ActionAllStarsMovie(Action):
    def name(self) -> Text:
        return "action_all_stars_movie"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("I'm in action_all_stars_movie")
        events = []
        movie_slot = tracker.get_slot("movie")
        movie_name = movie_slot
        movie_raw = next(tracker.get_latest_entity_values("movie"), None)

        if movie_name is None and movie_raw is not None:
            movie_name = string.capwords(movie_raw)

        print(f"Movie name: {movie_name}")

        if movie_name:
            tmdb = Tmdb(TMDB_APIKEY)
            try:
                search_response = tmdb.search_movie(movie_name)
                botResponse = (
                    f"I wasn't able to find any actor for the movie {movie_name}."
                )
                if len(search_response["results"]) > 0:
                    movie = search_response["results"][0]
                    movie_name = movie["title"]
                    actors_list = tmdb.movie_credits(movie["id"])["cast"]
                    if actors_list:
                        actors = [
                            actor["name"]
                            for actor in sorted(
                                actors_list, key=lambda x: x["popularity"], reverse=True
                            )[:5]
                        ]
                        botResponse = f"The actors starring in {movie['title']} are {get_printable_list(actors)}."
                botResponse += f"\nWould you like to know what {movie_name} is about?"
                events += [
                    SlotSet("last_question", "movie_plot"),
                    SlotSet("movie", movie_name),
                ]
                print(f"events in action_all_stars_movie: {events}")
            except Exception as ex:
                botResponse = ERROR_MESSAGE
                print(f"Exception: {movie_name}")
                events += [SlotSet("last_question", ""), SlotSet("movie", "")]
                # print(ex)
        else:
            botResponse = ERROR_MESSAGE
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        dispatcher.utter_message(text=botResponse)

        return events


class ActionDirector(Action):
    def name(self) -> Text:
        return "action_movie_director"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("I'm in action_movie_director")
        events = []
        movie_slot = tracker.get_slot("movie")
        movie_name = movie_slot
        movie_raw = next(tracker.get_latest_entity_values("movie"), None)
        directors = []

        if movie_name is None and movie_raw is not None:
            movie_name = string.capwords(movie_raw)

        if movie_name:
            print(f"movie_name: {movie_name}")
            tmdb = Tmdb(TMDB_APIKEY)
            try:
                search_response = tmdb.search_movie(movie_name)
                botResponse = f"I'm sorry! I wasn't able to find any results for the directors of {movie_name}."
                if len(search_response["results"]) > 0:
                    movie = search_response["results"][0]
                    movie_name = movie["title"]
                    print(f"movie: {movie}")
                    crew_list = tmdb.movie_credits(movie["id"])["crew"]
                    directors += [
                        person["name"]
                        for person in crew_list
                        if person["job"] == "Director"
                    ]
                    if len(directors) == 1:
                        botResponse = f"The director of {movie_name} is {get_printable_list(directors)}."
                    elif len(directors) >= 1:
                        botResponse = f"The directors of {movie_name} are {get_printable_list(directors)}."
                botResponse += (
                    f"\nWould you like to know who are the writers of {movie_name}?"
                )
                events += [
                    SlotSet("last_question", "movie_writer"),
                    SlotSet("movie", movie_name),
                ]
                print(f"events in action_movie_director: {events}")
            except Exception as ex:
                botResponse = ERROR_MESSAGE
                print(f"Exception: {movie_name}")
                events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        else:
            botResponse = ERROR_MESSAGE
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        dispatcher.utter_message(text=botResponse)

        return events


class ActionWriters(Action):
    def name(self) -> Text:
        return "action_movie_writer"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("I'm in action_movie_writer")
        events = []
        movie_slot = tracker.get_slot("movie")
        movie_name = movie_slot
        movie_raw = next(tracker.get_latest_entity_values("movie"), None)

        if movie_name is None and movie_raw is not None:
            movie_name = string.capwords(movie_raw)

        print(f"Movie name: {movie_name}")

        if movie_name:
            tmdb = Tmdb(TMDB_APIKEY)
            try:
                search_response = tmdb.search_movie(movie_name)
                botResponse = f"I'm sorry! I wasn't able to find any results for the writers of {movie_name}."
                if len(search_response["results"]) > 0:
                    movie = search_response["results"][0]
                    movie_name = movie["title"]
                    crew_list = tmdb.movie_credits(movie["id"])["crew"]
                    writers = set(
                        [
                            person["name"]
                            for person in sorted(
                                crew_list, key=lambda x: x["popularity"], reverse=True
                            )
                            if person["job"] == "Writer"
                        ][:3]
                    )
                    if len(writers) == 0:
                        writers.update(
                            [
                                person["name"]
                                for person in sorted(
                                    crew_list,
                                    key=lambda x: x["popularity"],
                                    reverse=True,
                                )
                                if person["job"] == "Screenplay"
                            ][:3]
                        )
                    if len(writers) == 1:
                        botResponse = f"Okay! The writer of {movie_name} is {get_printable_set(writers)}."
                    elif len(writers) >= 1:
                        botResponse = f"Okay! The writers of {movie_name} are {get_printable_set(writers)}."
                botResponse += (
                    f"\nWould you like to know where you can find {movie_name}?"
                )
                events += [
                    SlotSet("last_question", "movie_provider"),
                    SlotSet("movie", movie_name),
                ]
                print(f"events in action_movie_writer: {events}")
            except Exception as ex:
                botResponse = ERROR_MESSAGE
                print(f"Exception: {movie_name}")
                events += [SlotSet("last_question", ""), SlotSet("movie", "")]
                # print(ex)
        else:
            botResponse = ERROR_MESSAGE
            print(f"{movie_name}")
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        dispatcher.utter_message(text=botResponse)

        return events


class ActionPersonInfo(Action):
    def name(self) -> Text:
        return "action_person_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("I'm in action_person_info")

        events = []
        relevant_roles = {"Producer", "Director", "Art Director", "Writer"}
        person_raw = next(tracker.get_latest_entity_values("person"), None)
        print(person_raw)

        if person_raw:
            person_name = string.capwords(person_raw)
            tmdb = Tmdb(TMDB_APIKEY)
            try:
                search_response = tmdb.search_people(person_name)
                if search_response["total_results"] != 0:
                    person = search_response["results"][0]
                    person_id = person["id"]
                    person_details = tmdb.person_details(person_id)
                    print(person_details["name"])
                    roles = (
                        {"Actor"}
                        if tmdb.person_movie_credits(person_id)["cast"]
                        else {}
                    )
                    all_role_actor = {
                        item["job"]
                        for item in tmdb.person_movie_credits(person_id)["crew"]
                    }
                    roles.update(all_role_actor.intersection(relevant_roles))
                    botResponse = f"Alright! {person_details['name']} is a {get_printable_set(roles)}"

                    known_for = [
                        item["title"]
                        for item in person["known_for"][:3]
                        if item.get("title")
                    ]
                    if known_for:
                        known_phrase = get_printable_list(known_for)
                        botResponse += (
                            f". {person_details['name']} is known for {known_phrase}."
                        )
                        movie_name = known_for[0]
                        botResponse += (
                            f"\nWould you like to know where to find {movie_name}?"
                        )
                        events += [
                            SlotSet("last_question", "movie_provider"),
                            SlotSet("movie", movie_name),
                        ]
                        print(f"events in action_movie_writer: {events}")
                    elif person_details["birthday"]:
                        birthday_datetime = datetime.fromisoformat(
                            person_details["birthday"]
                        )
                        printable_birthday = birthday_datetime.strftime("%B, %d of %Y")
                        botResponse += f" born {printable_birthday}."
                        events += [SlotSet("last_question", ""), SlotSet("movie", "")]
                else:
                    botResponse = f"I'm sorry but I wasn't able to find any results for {person_name}."
                    events += [SlotSet("last_question", ""), SlotSet("movie", "")]
            except Exception as ex:
                botResponse = ERROR_MESSAGE
                print(f"Exception: {person_name}")
                events += [SlotSet("last_question", ""), SlotSet("movie", "")]
        else:
            botResponse = ERROR_MESSAGE
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]
        dispatcher.utter_message(text=botResponse)

        return events


class ActionPlot(Action):
    def name(self) -> Text:
        return "action_movie_plot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        events = []
        movie_slot = tracker.get_slot("movie")
        movie_name = movie_slot
        movie_raw = next(tracker.get_latest_entity_values("movie"), None)

        if movie_name is None and movie_raw is not None:
            movie_name = string.capwords(movie_raw)

        print(f"Movie name: {movie_name}")

        if movie_name:
            print("I'm in action_movie_plot")
            tmdb = Tmdb(TMDB_APIKEY)
            try:
                search_response = tmdb.search_movie(movie_name)
                botResponse = f"I'm sorry but I wasn't able to find any results for {movie_name} plot."
                if len(search_response["results"]) > 0:
                    movie_obj = tmdb.search_movie(movie_name)["results"][0]
                    movie_name = movie_obj["title"]
                    plot = movie_obj["overview"]
                    print("here")
                    if plot:
                        print("here2")
                        n_phrases = 2
                        parser = PlaintextParser.from_string(plot, Tokenizer("english"))
                        stemmer = Stemmer("english")
                        summarizer = Summarizer(stemmer)
                        summarizer.stop_words = get_stop_words("english")
                        summary = ""
                        for sentence in summarizer(parser.document, n_phrases):
                            sent = str(sentence) + " "
                            summary += sent
                        botResponse = f"Here's the summary of {movie_name}: {summary}"
                        botResponse += (
                            f"\nWould you like to know how {movie_name} is rated?"
                        )
                        events += [
                            SlotSet("last_question", "movie_reviews"),
                            SlotSet("movie", movie_name),
                        ]
                        print(f"events in action_movie_plot: {events}")
            except Exception as ex:
                botResponse = ERROR_MESSAGE
                print(f"Exception: {movie_name}")
                events += [SlotSet("last_question", ""), SlotSet("movie", "")]
        else:
            botResponse = ERROR_MESSAGE
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        dispatcher.utter_message(text="Ok let see...")
        dispatcher.utter_message(text=botResponse)

        return events


class ActionMovieReviews(Action):
    RATERS_DATA = {
        "imDb": {
            "normalizer": lambda x: x,
            "name": "IMDB",
        },
        "metacritic": {
            "normalizer": lambda x: x / 10,
            "name": "Metacritic",
        },
        "rottenTomatoes": {
            "normalizer": lambda x: x / 10,
            "name": "Rotten Tomatoes",
        },
        "filmAffinity": {
            "normalizer": lambda x: x,
            "name": "Film Affinity",
        },
    }

    def name(self) -> Text:
        return "action_movie_reviews"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("I'm in action_movie_reviews")

        events = []
        movie_slot = tracker.get_slot("movie")
        movie_name = movie_slot
        movie_raw = next(tracker.get_latest_entity_values("movie"), None)

        if movie_name is None and movie_raw is not None:
            movie_name = string.capwords(movie_raw)

        print(f"Movie name: {movie_name}")

        if movie_name:
            tmdb = Tmdb(TMDB_APIKEY)
            imdb = Imdb(IMDB_APIKEY)

            try:
                search_response = tmdb.search_movie(movie_name)
                botResponse = (
                    f"I wasn't able to find any ratings for the movie {movie_name}."
                )
                if len(search_response["results"]) > 0:
                    movie_obj = tmdb.search_movie(movie_name)["results"][0]
                    movie_name = movie_obj["title"]
                    movie_details = tmdb.movie_details(movie_obj["id"])

                    if movie_details["status"] == "Released":
                        tmdb_vote_average = movie_details["vote_average"]

                        imdb_movie_id = tmdb.external_id(movie_obj["id"])["imdb_id"]
                        raw_ratings = imdb.movie_ratings(imdb_movie_id)
                        ratings = []
                        raters = []
                        print("here")
                        for rater, rater_data in self.RATERS_DATA.items():
                            rating = raw_ratings[rater]
                            if rating:
                                ratings.append(rater_data["normalizer"](float(rating)))
                                raters.append(rater_data["name"])
                        print("Here 2")

                        botResponse = f"Ok. {movie_name} is rated on TMDB with {tmdb_vote_average}."
                        if ratings:
                            botResponse += f" It is rated as {mean(ratings):.1f} out of 10 as the average of {get_printable_list(raters)}"

                    elif movie_details["status"] == "Canceled":
                        botResponse = {f"Sadly {movie_name} has been cancelled."}
                    else:
                        botResponse = f"Mmm.. It seems that {movie_name} hasn't come out yet so there are no reviews."
                        if movie_details["release_date"]:
                            release_datetime = datetime.fromisoformat(
                                movie_details["release_date"]
                            )
                            printable_birthday = release_datetime.strftime(
                                "%B, %d of %Y"
                            )
                            botResponse += (
                                f" It will be released on {printable_birthday}."
                            )
                botResponse += (
                    f"\nWould you like to know who is the director of {movie_name}?"
                )
                events += [
                    SlotSet("last_question", "movie_director"),
                    SlotSet("movie", movie_name),
                ]
                print(f"events in action_movie_reviews: {events}")
            except Exception as ex:
                botResponse = ERROR_MESSAGE
                events += [SlotSet("last_question", ""), SlotSet("movie", "")]
                print(f"Exception: {movie_name}")
                print(ex)
        else:
            botResponse = ERROR_MESSAGE
            events += [SlotSet("last_question", ""), SlotSet("movie", "")]

        dispatcher.utter_message(text=botResponse)

        return events
