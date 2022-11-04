from app import app
from config import mysql
import requests
import pymysql
from flask import flash, json, jsonify, request

HOST = "127.0.0.1"
PORT = 8080
OMDB_API_KEY = "c37e6c14"


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


@app.route("/api/v1/search")
def get_movie_from_omdb():
    global response
    omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"
    if "title" and "year" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"] + "&y=" + request.args["year"]).json()
    elif "title" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"]).json()
    import_movie_from_omdb(response)
    return response


def import_movie_from_omdb(response):
    _json = response
    _title = _json["Title"]
    _year = _json["Year"]
    _directors = _json["Director"]
    _genre = _json["Genre"]
    _actors = _json["Actors"]
    _language = _json["Language"]
    _awards = _json["Awards"]
    _poster = _json["Poster"]
    _imdb_id = _json["imdbID"]
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sqlQuery = "INSERT INTO movies(title, year, directors, genre, actors, language, awards, poster, imdb_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    bindData = (_title, _year, _directors, _genre, _actors, _language, _awards, _poster, _imdb_id)
    cursor.execute(sqlQuery, bindData)
    conn.commit()
    cursor.close()
    conn.close()
    respone = jsonify('Test')
    respone.status_code = 200
    return respone

@app.post("/api/v1/movies")
def create_movie():
    if request.is_json:
        _json = request.json
        _title = _json["Title"]
        _year = _json["Year"]
        _directors = _json["Director"]
        _genre = _json["Genre"]
        _actors = _json["Actors"]
        _language = _json["Language"]
        _awards = _json["Awards"]
        _poster = _json["Poster"]
        _imdb_id = _json["imdbID"]
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sqlQuery = "INSERT INTO movies(title, year, directors, genre, actors, language, awards, poster, imdb_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        bindData = (_title, _year, _directors, _genre, _actors, _language, _awards, _poster, _imdb_id)
        cursor.execute(sqlQuery, bindData)
        conn.commit()
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
