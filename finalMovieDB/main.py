from app import app
from config import mysql
import csv
import requests
import pymysql
from flask import flash, json, jsonify, request

HOST = "127.0.0.1"
PORT = 8080
OMDB_API_KEY = "c37e6c14"
OMDB_URL = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"


def import_movie_from_json(movie_data):
    title = movie_data.get("Title") or movie_data.get("title")
    year = movie_data.get("Year") or movie_data.get("year") or ""
    directors = movie_data.get("Director") or movie_data.get("directors") or ""
    genre = movie_data.get("Genre") or movie_data.get("genre") or ""
    actors = movie_data.get("Actors") or movie_data.get("actors") or ""
    language = movie_data.get("Language") or movie_data.get("language") or ""
    awards = movie_data.get("Awards") or movie_data.get("awards") or "N/A"
    poster = movie_data.get("Poster") or movie_data.get("poster") or ""
    imdb_id = movie_data.get("imdbID") or movie_data.get("imdb_id") or ""
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql_query = "INSERT INTO movies(title, year, directors, genre, actors, language, awards, poster, imdb_id) VALUES(" \
                "%s, %s, %s, %s, %s, %s, %s, %s, %s) "
    bind_data = (title, year, directors, genre, actors, language, awards, poster, imdb_id)
    cursor.execute(sql_query, bind_data)
    conn.commit()
    if imdb_id == "":
        cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                       "WHERE title = %s", title)
    else:
        cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                       "WHERE imdb_id = %s", imdb_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return movie_data


def get_movie_data_from_database_with_imdb_id_helper(imdb_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE imdb_id = %s", imdb_id)
    movie_data = cursor.fetchone()
    return movie_data


def get_movie_data_from_database_with_id_helper(movie_id: int):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE id = %s", movie_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return movie_data


def get_movie_data_from_database_with_title_helper(title):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies "
                   "WHERE title = %s", title)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return movie_data


def get_imdb_id_from_json(movie_data):
    return movie_data["imdbID"]


def get_movie_data_from_omdb_with_title(movie_title):
    return requests.get(OMDB_URL + "&t=" + movie_title).json()


def get_movie_data_from_omdb_with_imdb_id(imdb_id):
    return requests.get(OMDB_URL + "&i=" + imdb_id).json()


@app.route("/api/v1/search")
def search():
    if "title" in request.args and request.args["title"] != "":
        movie_data = get_movie_data_from_database_with_title_helper(request.args["title"])
        if movie_data is None:
            imdb_movie_data = get_movie_data_from_omdb_with_title(request.args["title"])
            imdb_id = imdb_movie_data["imdbID"]
            movie_data_with_imdb_id = get_movie_data_from_database_with_imdb_id_helper(imdb_id)
            if movie_data_with_imdb_id is None:
                return jsonify(import_movie_from_json(imdb_movie_data))
            else:
                return jsonify(movie_data_with_imdb_id)
        return jsonify(movie_data)
    else:
        return jsonify({"error": "malformed request, no title parameter is found"}), 400


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
    movie_data = get_movie_data_from_database_with_id_helper(movie_id)
    if movie_data is None:
        return jsonify({"error": f"no movie found for id ({movie_id})"}), 404
    return jsonify(movie_data)


@app.post("/api/v1/movies")
def create_movie():
    if request.is_json:
        if "imdbID" in request.json or "imdb_id" in request.json:
            json_imdb_id = request.json.get("imdbID") or request.json.get("imdb_id")
            movie_data = get_movie_data_from_database_with_imdb_id_helper(json_imdb_id)
            if movie_data is None:
                return jsonify(import_movie_from_json(get_movie_data_from_omdb_with_imdb_id(json_imdb_id))), 200
            else:
                return jsonify(movie_data), 200
        elif "Title" in request.json or "title" in request.json:
            return import_movie_from_json(request.json)
        else:
            return jsonify({"error": "malformed request, missing required fields"}), 400
    else:
        return jsonify({"error": "request must be json"}), 415


@app.put("/api/v1/movies/<int:movie_id>")
def update_movie_data_in_database(movie_id: int):
    if request.is_json:
        original_movie_data = get_movie_data_from_database_with_id_helper(movie_id)
        if original_movie_data is None:
            return jsonify({"error": f"no movie found for id ({movie_id})"}), 404
        if "Title" in request.json or "title" in request.json or "Year" in request.json or "year" in request.json or "Director" in request.is_json or "directors" in request.json or "Genre" in request.json or "genre" in request.json or "Actors" in request.json or "actors" in request.json or "Language" in request.json or "language" in request.json or "Awards" in request.json or "awards" in request.json or "Poster" in request.json or "poster" in request.json or "imdbID" in request.json or "imdb_id" in request.json:
            movie_data = {}
            movie_data["title"] = request.json.get("Title") or request.json.get("title") or original_movie_data["title"]
            movie_data["year"] = request.json.get("Year") or request.json.get("year") or original_movie_data["year"]
            movie_data["directors"] = request.json.get("Director") or request.json.get("directors") or original_movie_data["directors"]
            movie_data["genre"] = request.json.get("Genre") or request.json.get("genre") or original_movie_data["genre"]
            movie_data["actors"] = request.json.get("Actors") or request.json.get("actors") or original_movie_data["actors"]
            movie_data["language"] = request.json.get("Language") or request.json.get("language") or original_movie_data["language"]
            movie_data["awards"] = request.json.get("Awards") or request.json.get("awards") or original_movie_data["awards"]
            movie_data["poster"] = request.json.get("Poster") or request.json.get("poster") or original_movie_data["poster"]
            movie_data["imdb_id"] = request.json.get("imdbID") or request.json.get("imdb_id") or original_movie_data["imdb_id"]
            sql_query = "UPDATE movies SET title=%s, year=%s, directors=%s, genre=%s, actors=%s, language=%s, awards=%s, poster=%s, imdb_id=%s WHERE id=%s"
            bind_data = (movie_data["title"], movie_data["year"], movie_data["directors"], movie_data["genre"], movie_data["actors"], movie_data["language"], movie_data["awards"], movie_data["poster"], movie_data["imdb_id"], movie_id)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql_query, bind_data)
            conn.commit()
        return jsonify(movie_data)
    else:
        return jsonify({"error": "request must be json"}), 415


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
    return jsonify(result)


@app.get("/api/v1/academy-awards/best-pictures/<int:year>")
def get_academy_awards_best_picture_winner(year: int):
    with open("csvs/the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year and row[6] == "True" and (row[3] == "OUTSTANDING PICTURE" or row[3] == "BEST PICTURE"):
                movie_title = row[5]
                data = dict(zip(header, row))
                movie_data = get_movie_data_from_database_with_title_helper(movie_title)
                if movie_data is None:
                    movie_data = import_movie_from_json(get_movie_data_from_omdb_with_title(movie_title))
                    data["movie_data"] = movie_data
                else:
                    data["movie_data"] = movie_data
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
                movie_data = get_movie_data_from_database_with_title_helper(movie_title)
                if movie_data is None:
                    movie_data = import_movie_from_json(get_movie_data_from_omdb_with_title(movie_title))
                    data["movie_data"] = movie_data
                else:
                    data["movie_data"] = movie_data
                result.append(data)
    if not result:
        return {"error": f"no data found for best actors in this year ({year})"}, 404
    return jsonify(result)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
