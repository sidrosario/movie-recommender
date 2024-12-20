from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        #recommendations = recommend_movies(user_input)
        recommendations = ['Godfather', 'Shawshank Redemption', 'Pulp Fiction']
        return render_template("index.html", recommendations=recommendations, user_input=user_input)
    return render_template("index.html", recommendations=None)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
