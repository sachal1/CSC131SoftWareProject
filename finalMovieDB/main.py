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
OMDB_URL = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"


def import_movie_from_json(original_movie_data):
    _json = original_movie_data
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
    sql_query = "INSERT INTO movies(title, year, directors, genre, actors, language, awards, poster, imdb_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    bind_data = (_title, _year, _directors, _genre, _actors, _language, _awards, _poster, _imdb_id)
    cursor.execute(sql_query, bind_data)
    conn.commit()
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE imdb_id = %s", _imdb_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return movie_data


def is_imdb_id_existed_in_database(imdb_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE imdb_id = %s", imdb_id)
    movie_data = cursor.fetchone()
    if movie_data is None:
        return 0
    else:
        return jsonify(movie_data)


def is_title_existed_in_database(title):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE title = %s", title)
    movie_data = cursor.fetchone()
    if movie_data is None:
        return 0
    else:
        return jsonify(movie_data)


def get_imdb_id_from_json(movie_data):
    return movie_data["imdbID"]


def get_movie_data_from_omdb_with_title(movie_title):
    return requests.get(OMDB_URL + "&t=" + movie_title).json()


def get_movie_data_from_omdb_with_imdb_id(imdb_id):
    return requests.get(OMDB_URL + "&i=" + imdb_id).json()


@app.route("/api/v1/search")
def search():
    if "title" in request.args:
        response = get_movie_data_from_omdb_with_title(request.args["title"])
        imdb_id = response["imdbID"]
        movie_data = is_imdb_id_existed_in_database(imdb_id)
        if movie_data == 0:
            return import_movie_from_json(response)
        else:
            return movie_data
    else:
        return {"error": "malformed request, no title parameter is found"}, 400


@app.get("/api/v1/movies")
def get_all_movies_data_from_database():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    rows_count = cursor.execute("SELECT * FROM movies")
    if rows_count > 0:
        movies_data = cursor.fetchall()
    cursor.close()
    conn.close()
    if rows_count == 0:
        return {"error": "there is no movie in the database"}, 404
    return jsonify(movies_data), 200


@app.get("/api/v1/movies/<int:movie_id>")
def get_movie_data_from_database(movie_id: int):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE id = %s", movie_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if movie_data is None:
        return {"error": f"no movie found for id ({movie_id})"}, 404
    return jsonify(movie_data), 200


@app.post("/api/v1/movies")
def create_movie():
    if request.is_json:
        # if "imdbID" in request.json:
        #    imdb_id = request.json.get("imdbID")
        #    movie_data = is_imdb_id_existed_in_database(imdb_id)
        #    if movie_data == 0:
        #        return import_movie_from_json(get_movie_data_from_omdb_with_imdb_id(imdb_id))
        #    else:
        #        return {"error": f"movie with IMDb ({imdb_id}) already existed in the database"}, 200
        # else:
        #    return import_movie_from_json(request.json)
        return import_movie_from_json(request.json)


@app.put("/api/v1/movies/<int:movie_id>")
def update_movie_data_in_database(movie_id: int):
    return 0


# This method takes movie_id as parameter and delete the movie matched that id.
@app.delete("/api/v1/movies/<int:movie_id>")
def delete_movie(movie_id: int):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = %s", movie_id)
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": f"movie {movie_id} has been deleted from the database"}, 200


# This function will return all academy awards nominees
@app.get("/api/v1/academy-awards/<int:year>")
def get_academy_awards_nominees(year: int):
    result = []
    with open("csvs/the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year:
                result.append(dict(zip(header, row)))
    if not result:
        return {"error": f"no data found for this year ({year})"}, 404
    return json.dumps(result)


@app.get("/api/v1/academy-awards/best-pictures/<int:year>")
def get_academy_awards_best_picture_winner(year: int):
    with open("csvs/the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year and row[6] == "True" and (row[3] == "OUTSTANDING PICTURE" or row[3] == "BEST PICTURE"):
                movie_title = row[5]
                data = dict(zip(header, row))
                movie_data = is_title_existed_in_database(movie_title)
                if movie_data == 0:
                    movie_data = import_movie_from_json(get_movie_data_from_omdb_with_title(movie_title))
                    data["movie_data"] = movie_data
                else:
                    data["movie_data"] = movie_data.json
                return jsonify(data)
    return {"error": f"no data found for best picture in this year ({year})"}, 404


@app.get("/api/v1/academy-awards/best-actors/<int:year>")
def get_academy_awards_best_actor_winner(year: int):
    with open("csvs/the_oscar_award.csv") as f:
        result = []
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year and row[6] == "True" and (row[3] == "ACTOR" or row[3] == "ACTRESS" or row[3] == "ACTOR IN A LEADING ROLE" or row[3] == "ACTRESS IN A LEADING ROLE"):
                movie_title = row[5]
                data = dict(zip(header, row))
                movie_data = is_title_existed_in_database(movie_title)
                if movie_data == 0:
                    movie_data = import_movie_from_json(get_movie_data_from_omdb_with_title(movie_title))
                    data["movie_data"] = movie_data
                else:
                    data["movie_data"] = movie_data.json
                result.append(data)
    if not result:
        return {"error": f"no data found for best actors in this year ({year})"}, 404
    return jsonify(result)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
