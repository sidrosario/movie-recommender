from flask import Flask, render_template, request
from TMDBService import TMDBService
from database import add_movies_links
from main import find_recommendations

app = Flask(__name__)

def add_poster_url(recommendations):
    tm = TMDBService()
    for movie in recommendations:
        tmdb_id = tm.get_tmdb_id(movie['imdb_id'])
        poster_url = tm.get_poster_url(tmdb_id)
        movie['poster_url'] = poster_url

def add_fields(recommendations):
    add_movies_links(recommendations)
    add_poster_url(recommendations)

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    movie_links = []
    user_input = ""
    if request.method == 'POST':
        user_input = request.form['user_input']
        recommendations = find_recommendations(user_input)
        add_fields(recommendations)  # Use new function

    return render_template('recommendations.html', recommendations=recommendations,user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)