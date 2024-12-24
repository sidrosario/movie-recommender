from flask import Flask, render_template, request
from database import add_movies_links
from main import find_recommendations

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    movie_links = []
    user_input = ""
    if request.method == 'POST':
        user_input = request.form['user_input']
        recommendations = find_recommendations(user_input)
        add_movies_links(recommendations)  # Use new function

    return render_template('recommendations.html', recommendations=recommendations,user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)