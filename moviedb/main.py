from app import app
from config import mysql
import requests
import pymysql
from flask import flash, jsonify, request

HOST = "127.0.0.1"
PORT = 8080
OMDB_API_KEY = "c37e6c14"


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


@app.route("/api/v1/search")
def get_movie_from_omdb():
    omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"
    if "title" and "year" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"] + "&y=" + request.args["year"]).json()
    elif "title" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"]).json()
    return response


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
