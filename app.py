from flask import Flask, render_template, request
from TMDBService import TMDBService
from database import attach_imdb_links
from main import find_recommendations

app = Flask(__name__)


def add_movie_details(recommendations):
    tm = TMDBService()
    for movie in recommendations:
        tmdb_id = tm.get_tmdb_id(movie['imdb_id'])
        if tmdb_id:
            details = tm.get_movie_poster_rating_overview(tmdb_id)
            if details:
                movie.update(details)

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    user_input = ""
    if request.method == 'POST':
        user_input = request.form['user_input']
        recommendations = find_recommendations(user_input)
        attach_imdb_links(recommendations)
        add_movie_details(recommendations)

    return render_template('recommendations.html', recommendations=recommendations, user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)