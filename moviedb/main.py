from app import app
from config import mysql
import csv
import requests
# import pandas
import pymysql
from flask import flash, json, jsonify, request

HOST = "127.0.0.1"
PORT = 8080
OMDB_API_KEY = "c37e6c14"
omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


# This function take a json as parameter and add it to the movies table.
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
    response = jsonify('Test')
    response.status_code = 200
    return response


# This method checking if the movie is already exits in the database using imdbID as parameter
def is_movie_exist_in_database(imdb_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE imdb_id = %s", imdb_id)
    movie_data = cursor.fetchone()
    if movie_data is None:
        return 0
    else:
        return jsonify(movie_data)


# This method take movie title (and year) and parameter and return its data
@app.route("/api/v1/search")
def get_movie_from_omdb():
    global response
    #omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"
    if "title" and "year" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"] + "&y=" + request.args["year"]).json()
    elif "title" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"]).json()
    imdb_id = response["imdbID"]
    movie_data = is_movie_exist_in_database(imdb_id)
    # Need further implementation to checking if the imdbID is already in the database
    if movie_data == 0:
        import_movie_from_omdb(response)
    else:
        return movie_data
    return response


# This method take the movie_id as parameter, searching through MySQL and return data of matching movie
@app.get("/api/v1/movies/<int:movie_id>")
def get_movie_from_database(movie_id: int):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE id = %s", movie_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if movie_data is None:
        return {"error": f"No movie found for ID {movie_id}"}, 404
    else:
        return movie_data, 200


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


# This method takes movie_id as parameter and delete the movie matched that id.
@app.delete("/api/v1/movies/<int:movie_id>")
def delete_movie(movie_id: int):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = %s", movie_id)
        conn.commit()
        return {"success": f"Movie {movie_id} has been deleted from the database"}, 200
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.get("/api/v1/academy-awards/<int:year>")
def get_academy_awards_nominees(year: int):
    result = []
    with open("csvs/the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year:
                result.append(dict(zip(header, row)))
    return json.dumps(result)


@app.get("/api/v1/academy-awards/best-picture/<int:year>")
def get_academy_awards_best_picture_winner(year: int):
    with open("csvs/the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year and row[6] == "True" and (row[3] == "OUTSTANDING PICTURE" or row[3] == "BEST PICTURE"):
                movie_title = row[5]
    response = requests.get(omdb_url + "&t=" + movie_title).json()
    return response

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
