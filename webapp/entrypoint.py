from flask import Flask, request, jsonify
from whitehouse.database import search_articles

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# create a route to recieve a POST request with the query as string and return the articles
@app.route("/search", methods=["POST"])
def process_query():
    if request.is_json:
        data = request.get_json()
        query = data.get("query", "")

        if query:
            results = search_articles(query)
            return jsonify(results), 200
        else:
            return jsonify({"error": "No query provided"}), 400
    else:
        return jsonify({"error": "Request must be JSON"}), 400


def start():
    app.run(debug=True)
