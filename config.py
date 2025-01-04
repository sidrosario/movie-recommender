# a config file for the csv files.
DATASET_DIR = 'datasets/ml-latest-small'
CSV_FILES = {
    'movies': f'{DATASET_DIR}/movies.csv',
    'movies_extended': f'{DATASET_DIR}/movies_extended.csv',
    'ratings': f'{DATASET_DIR}/ratings.csv',
    'tags': f'{DATASET_DIR}/tags.csv',
    'links': f'{DATASET_DIR}/links.csv',
    'keywords': f'{DATASET_DIR}/keywords.csv',
    'actors': f'{DATASET_DIR}/actors.csv',
    'director_overview': f'{DATASET_DIR}/director_overview.csv',
    'movie_ratings': f'{DATASET_DIR}/movie_ratings.csv',
    'movie_popularity': f'{DATASET_DIR}/movie_popularity.csv'
}
LOGS_DIR = 'logs'
LOG_FILES = {
    'db' : f'{LOGS_DIR}/db.log',
}
USER_REQUESTS = [
    "A Christopher Nolan thriller movie",
    "A movie on drug addiction",
    "Something about the Holocaust",
    "A horror movie, with psychological depth, eerie settings, and a suspenseful build-up.",
    "A sci-fi movie that explores futuristic technology, space travel, and the complexities of human emotions.",
    "an epic historical drama, filled with battles, political intrigue.",
    "an animated movie suitable for adults, with a complex plot, and deep character development.",
    "a musical, but not a romance or an animation, with catchy songs, and dance sequences.",
    "a murder mystery which is not scary",
    "A mystery movie starring Bruce Willis",
    "An action packed fantasy movie, with a great soundtrack",
    "a heartwarming comedy set with witty dialogue and charming characters.",
    "a movie about being a mother. Not a comedy",
    "a romantic comedy about Christmas.",
    "a movie about being lonely",
    "---",
    "a movie on prisons and friendships",
    "A romantic comedy starring Julia roberts",
    "a sci fi movie with inter planetary space travel",
    "a horror movie starring jack nicholson",
    "a serious film about drug addiction",
    "a movie about the holocaust",
    "a movie on prison escape",
    "an epic historical drama, with battles",
    ""

]
DB_LOCATION='sqlite:///movies.db'

NUM_SEARCH_RESULTS = 5

GENRES="Drama, War, Animation, Mystery, Fantasy, Children, Documentary, Film-Noir, Sci-Fi, Adventure, Horror, Western, Action, Crime, Comedy, Musical, Romance, Thriller."