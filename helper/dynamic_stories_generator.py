import random

INTENTS_TEMPLATE = {
    "movie_provider": [
        "I want to watch {movie}, where can I find it?",
        "Find where I can watch {movie}",
        "Can you find where i can watch {movie}?",
        "Please tell me where I can find {movie}",
    ],
    "all_stars_movie": [
        "Who acted in {movie}?",
        "Who starred in {movie}?",
        "Who played in {movie}?",
        "Do you know who played in {movie}?",
    ],
    "movie_director": [
        "I'd like to know who directed {movie}",
        "Can you tell me who directed {movie}?",
        "May I know who directed {movie}?",
        "In the movie {movie} who directed?",
    ],
    "movie_writer": [
        "I'd like to know who wrote {movie}",
        "Do you know who wrote {movie}?",
        "Can you tell me who wrote {movie}?",
        "In the movie {movie} who was the writer?",
    ],
    "person_info": [
        "Do you know anything about {person}?",
        "May I know something about {person}?",
        "Can you tell me something about {person}?",
        "Could you please tell me something about {person}?",
    ],
    "movie_plot": [
        "Do you know what is the plot of {movie}?",
        "May I know what is the movie {movie} about?",
        "Can you tell me what is the plot of {movie}?",
        "Can you find what does this movie talk about?",
    ],
    "movie_reviews": [
        "Do you know what are the reviews of {movie}?",
        "May I know what are the reviews of {movie}?",
        "Can you tell me what are the reviews of {movie}?",
        "Can you find the movie {movie} is rated?",
    ],
    "out_of_scope": [
        "What's the weather like?",
        "Where is your happy place?",
        "What is your nickname?",
        "What is your favorite color?",
        "What is your favorite food?",
        "What four words best describe you?",
        "When did you feel safest?",
        "Can you bring me to Trento?",
    ],
}

random.seed(10)

out = open("tests/dynamic_stories.yml", "w")
out.write("stories:\n")

actors = ["Angelina Jolie", "Brad Pitt", "Leonardo DiCaprio", "Tom Cruise", "Tom Hanks"]

for i, movie in enumerate(
    [
        "Encanto",
        "Fight Club",
        "Inception",
        "Interstellar",
        "Psycho",
        "The Lion King",
        "Whiplash",
        "City lights",
        "The Prestige",
        "Casablanca",
        "Alien",
    ]
):
    out.writelines(
        [
            f"\n- story: all {i}\n",
            "  steps:\n",
            "    - user: |\n",
            "        hi\n",
            "      intent: greet\n",
            "    - action: utter_greet\n",
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['out_of_scope'])}\n",
            "      intent: out_of_scope\n",
            "    - action: utter_out_of_scope\n",
            "    - slot_was_set:\n",
            '        - last_question: ""\n',
            f'        - movie: ""\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['person_info']).format(person=random.choice(actors))}\n",
            "      intent: person_info\n",
            "    - action: action_person_info\n",
            "    - slot_was_set:\n",
            '        - last_question: "movie_provider"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['movie_provider']).format(movie=movie)}\n",
            "      intent: movie_provider\n",
            "    - action: action_movie_provider\n",
            "    - slot_was_set:\n",
            '        - last_question: "all_stars_movie"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['all_stars_movie']).format(movie=movie)}\n",
            "      intent: all_stars_movie\n",
            "    - action: action_all_stars_movie\n",
            "    - slot_was_set:\n",
            '        - last_question: "movie_plot"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['out_of_scope'])}\n",
            "      intent: out_of_scope\n",
            "    - action: utter_out_of_scope\n",
            "    - slot_was_set:\n",
            '        - last_question: ""\n',
            f'        - movie: ""\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['movie_plot']).format(movie=movie)}\n",
            "      intent: movie_plot\n",
            "    - action: action_movie_plot\n",
            "    - slot_was_set:\n",
            '        - last_question: "movie_reviews"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['movie_reviews']).format(movie=movie)}\n",
            "      intent: movie_reviews\n",
            "    - action: action_movie_reviews\n",
            "    - slot_was_set:\n",
            '        - last_question: "movie_director"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['out_of_scope'])}\n",
            "      intent: out_of_scope\n",
            "    - action: utter_out_of_scope\n",
            "    - slot_was_set:\n",
            '        - last_question: ""\n',
            f'        - movie: ""\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['movie_director']).format(movie=movie)}\n",
            "      intent: movie_director\n",
            "    - action: action_movie_director\n",
            "    - slot_was_set:\n",
            '        - last_question: "movie_writer"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            f"        {random.choice(INTENTS_TEMPLATE['movie_writer']).format(movie=movie)}\n",
            "      intent: movie_writer\n",
            "    - action: action_movie_writer\n",
            "    - slot_was_set:\n",
            '        - last_question: "movie_provider"\n',
            f'        - movie: "{movie}"\n',
            "    - user: |\n",
            "        no thanks\n",
            "      intent: deny\n",
            "    - action: action_deny\n",
            "    - slot_was_set:\n",
            '        - last_question: ""\n',
            '        - movie: ""\n',
            "    - user: |\n",
            "        goodbye\n",
            "      intent: goodbye\n",
            "    - action: utter_goodbye\n",
        ]
    )
