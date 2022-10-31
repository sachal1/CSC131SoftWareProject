#
import json

import simplejson
from flask import Flask, request, jsonify, make_response
import requests
import simplejson as json

# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

HOST = "127.0.0.1"
PORT = 8080

OMDB_API_KEY = "c37e6c14"


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


# Searching the OMDb database via title and year.
@app.route("/search")
def get_movie_from_omdb():
    omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"

    # If title is in the request, curl the OMDb database with title parameter.
    if "title" and "year" in request.args:

        # Get the response from OMDB and set it to response
        response = requests.get(omdb_url + "&t=" + request.args["title"] + "&y=" + request.args["year"]).text

    elif "title" in request.args:

        # Get the response from OMDB and set it to response
        response = requests.get(omdb_url + "&t=" + request.args["title"]).text

    # This part is not completed as convert the retrieved response back to JSON causing Unicode character.
    response = simplejson.loads(response, "utf-8")

    # Here, may need a way to add the response to database.

    # Return the response.
    return response


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
