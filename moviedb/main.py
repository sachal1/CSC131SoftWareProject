from app import app
from config import mysql
import csv
import requests
# import pandas
import pymysql
from flask import flash, json, jsonify, request, render_template, redirect

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
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE imdb_id = %s", _imdb_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return movie_data


def is_imdb_id_existed_in_database(imdb_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE imdb_id = %s", imdb_id)
    movie_data = cursor.fetchone()
    if movie_data is None:
        return 0
    else:
        return jsonify(movie_data)


def is_title_existed_in_database(title):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE title = %s", title)
    movie_data = cursor.fetchone()
    if movie_data is None:
        return 0
    else:
        return jsonify(movie_data)


def get_imdb_id_from_json(movie_data):
    return movie_data["imdbID"]


def get_movie_data_from_omdb_with_title(movie_title):
    return requests.get(OMDB_URL + "&t=" + movie_title).json()


def get_movie_data_from_omdb_with_title_year(movie_title, year):
    return requests.get(OMDB_URL + "&t=" + movie_title + "&y=" + year).json()


def get_movie_data_from_omdb_with_imdb_id(imdb_id):
    return requests.get(OMDB_URL + "&i=" + imdb_id).json()


def append_movie_data_to_a_json(movie_tile):
    return 0


@app.route('/')
def home():
    return f'''
        <html>
            <body bgcolor="#FFD700">
                <h1 style="text-align: center; font-family: cursive; margin-top: 30%;">Movies</h1>
                <form style="text-align: center;" action="/movies" method="POST">
                    <input type="text" name="destination">
                    <input type="submit" value="Go">
                    
                </form>
            </body>
        </html>
    '''
    
@app.route('/movies', methods=['POST'])
def movies():
    # redirect to the URL entered by the user in the form
    return redirect(request.form['destination'])

@app.route("/api/v1/search")
def search():
    if "title" and "year" in request.args:
        response = get_movie_data_from_omdb_with_title_year(request.args["title"], request.args["year"])
    if "title" in request.args:
        response = get_movie_data_from_omdb_with_title(request.args["title"])
    imdb_id = response["imdbID"]
    movie_data = is_imdb_id_existed_in_database(imdb_id)
    if movie_data == 0:
        return import_movie_from_json(response)
    else:
        return movie_data


@app.get("/api/v1/movies/<int:movie_id>")
def get_movie_data_from_database(movie_id: int):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE id = %s", movie_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if movie_data is None:
        return {"error": f"no movie found for id ({movie_id})"}, 404
    else:
        return movie_data, 200

@app.get('/api/v1/getmovieshtml')
def printresult():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT * FROM movies"
    cursor.execute(query)
    results = cursor.fetchall()

    # Generate an HTML table from the movie data
    html = "<table>"
    for row in results:
        html += "<tr>"
        for key, value in row.items():
            html += "<td>{}</td>".format(value)
        html += "</tr>"
    html += "</table>"

    # Add a back button and set the background color to gold
    html += "<button onclick='window.history.back()'>Back</button>"
    html = "<body style='background-color: gold;'>" + html + "</body>"

    # Return the HTML page as the response
    return html



@app.route("/movieshtml/<int:movie_id>")
def get_movie_data_from_databasehtml(movie_id: int):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, year, directors, genre, actors, language, awards, poster, imdb_id FROM movies WHERE id = %s", movie_id)
    movie_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if movie_data is None:
        return "<html><body><p>No movie found for id ({movie_id})</p></body></html>", 404
    else:
        html_string = "<html><head><style>table { border-collapse: collapse; } table, th, td { border: 1px solid black; }</style></head><body bgcolor='#FFD700'>"
        html_string += "<table>"
        for key, value in movie_data.items():
            html_string += "<tr><th>" + key + "</th><td>" + str(value) + "</td></tr>"
        html_string += "</table></body></html>"

    
        # Add a button that will redirect the user to the home page when clicked
        html_string += "<button type='button' onclick='window.location.href = \"/\";'>Back To Homepage</button>"
        html_string += "</body></html>"

        html_string2 = html_string

        return html_string, 200


@app.post("/api/v1/createmovie")
def create_movie():
    if request.is_json:
        if "imdbID" in request.json:
            imdb_id = request.json.get("imdbID")
            movie_data = is_imdb_id_existed_in_database(imdb_id)
            if movie_data == 0:
                return import_movie_from_json(get_movie_data_from_omdb_with_imdb_id(imdb_id))
            else:
                return {"error": f"movie with IMDb ({imdb_id}) already existed in the database"}, 200
        else:
            return import_movie_from_json(request.json)

@app.route('/movie-form', methods=['GET', 'POST'])
def movie_form():
    if request.method == 'POST':
        # Extract the movie data from the form
        title = request.form['Title']
        directors = request.form["Director"]
        genre = request.form["Genre"]
        year = request.form['Year']
        actor = request.form['Actors']
        language = request.form["Language"]
        awards = request.form["Awards"]
        imdb_id = request.form["imdbID"]



        # Check if the movie already exists in the database
        if is_title_existed_in_database(title):
            return 'Movie already exists in database:'

        # Create a dictionary with the movie data
        movie_data = {
        'Title': title,
        'Year': year,
        'Actors': actor,
        'Director': directors,
        'Genre': genre,
        'Language': language,
        'Awards': awards,
        'imdbID': imdb_id
}
            
        
        # Import the movie into the database
        movie = import_movie_from_json(movie_data)

        return 'Movie data received and imported into database: {} ({}) starring {}, directed by {}, in the genre {}, with IMDB ID {}'.format(title, year, actor, directors, genre, imdb_id)

    # If the request is a GET request, return the HTML form
    return '''
        <form method="POST">
        <label>Title: <input type="text" name="title"></label><br>
        <label>Year: <input type="number" name="year"></label><br>
        <label>Actor: <input type="text" name="actor"></label><br>
        <label>Director: <input type="text" name="Director"></label><br>
        <label>Genre: <input type="text" name="Genre"></label><br>
        <label>Language: <input type="text" name="Language"></label><br>
        <label>Awards: <input type="text" name="Awards"></label><br>
        <label>IMDB ID: <input type="text" name="imdbID"></label><br>
        <input type="submit" value="Submit">
    </form>
'''



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

@app.delete("/api/v1/movieshtml/<int:movie_id>")
def delete_moviehtml(movie_id: int):

    # Retrieve the movie data for the deleted movie
    cursor.execute("SELECT * FROM movies WHERE id = %s", movie_id)
    deleted_movie = cursor.fetchone()
    cursor.close()
    conn.close()
   
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("DELETE FROM movies WHERE id = %s", movie_id)
    conn.commit()

    # Print the deleted movie data in an HTML table
    if deleted_movie:
        table = "<table><tr>"
        for key in deleted_movie:
            table += "<th>" + key + "</th>"
        table += "</tr><tr>"
        for value in deleted_movie.values():
            table += "<td>" + str(value) + "</td>"
        table += "</tr></table>"

        return table, 200
    else:
        return {"error": "No movie was found with the given ID"}, 404

# This function will return all academy awards nominees
@app.get("/api/v1/academy-awards/<int:year>")
def get_academy_awards_nominees(year: int):
    result = []
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year:
                result.append(dict(zip(header, row)))
    if not result:
        return {"error": f"no data found for this year ({year})"}, 404
    return json.dumps(result)

@app.get("/api/v1/htmlacademy-awards/<int:year>")
def get_academy_awards_nomineeshtml(year: int):
    result = []
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year:
                result.append(dict(zip(header, row)))
    if not result:
        return {"error": f"no data found for this year ({year})"}, 404

 # Create the HTML string
    html_str = "<table bgcolor='gold'>"
    for award in result:
        html_str += "<tr>"
        for key, value in award.items():
            html_str += "<td>{}: {}</td>".format(key, value)
        html_str += "</tr>"
    html_str += "</table>"
    html_str += "<button onclick='history.go(-1);'>Back</button><body bgcolor='#FFD700'>"

    # Return the HTML string
    return html_str



@app.get("/api/v1/academy-awards/best-pictures/<int:year>")
def get_academy_awards_best_picture_winner(year: int):
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
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

   
@app.get("/api/v1/htmlacademy-awards/best-pictures/<int:year>")
def get_academy_awards_best_picture_winnerhtml(year: int):
    movie_data = None
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
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

    html_table = "<table style='background-color: gold;'>"
    for key, value in data.items():
        html_table += "<tr><td>{}</td><td>{}</td></tr>".format(key, value)
    html_table += "</table>"
    html_table += "<button onclick='history.go(-1);'>Back</button><body bgcolor='#FFD700'>"

    return html_table

@app.get("/api/v1/academy-awards/best-actors/<int:year>")
def get_academy_awards_best_actor_winner(year: int):
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
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
    return jsonify(result)

@app.get("/api/v1/htmlacademy-awards/best-actors/<int:year>")
def get_academy_awards_best_actor_winnerhtml(year: int):
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
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
    html_table = "<table style='background-color: gold;'>"
    for key, value in data.items():
        html_table += "<tr><td>{}</td><td>{}</td></tr>".format(key, value)
    html_table += "</table>"
    html_table += "<button onclick='history.go(-1);'>Back</button><body bgcolor='#FFD700'>"

    return html_table



if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
