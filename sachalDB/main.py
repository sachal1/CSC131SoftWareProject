from app import app
from config import mysql
import csv
import requests
# import pandas
import pymysql
from flask import flash, json, jsonify, request, render_template


HOST = "127.0.0.1"
PORT = 8080
OMDB_API_KEY = "c37e6c14"
omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}"


@app.route("/foo")
def hello_world():
    return "Hello, World!"

@app.route("/table")    # Create tables fast - change as needed
def createtable():
    #cursor = mysql.connection.cursor()
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = ("CREATE TABLE extra(id INT NOT NULL AUTO_INCREMENT, title VARCHAR(255) , year VARCHAR(255), directors VARCHAR(255), genre VARCHAR(255), actors VARCHAR(255), language VARCHAR(255), awards VARCHAR(255), poster VARCHAR(255), imdb_id VARCHAR(255), primary key (id))") 
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return "table has been created"   

@app.route('/form') # connection tester - Login form sent via HTML to login to MYSQL 
def formtest():
    return render_template('form.html')

@app.route('/formtest') # connection tester - Login form sent via HTML to login to MYSQL 
def form():
    return render_template('movie.html')    

@app.route("/createtest")
def createtest():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query=("CREATE TABLE testname (name VARCHAR(255),age VARCHAR(255))")
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return "table has been created"    

@app.route('/login', methods = ['POST', 'GET']) # connection tester - Tester for flask DB - works 
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(''' INSERT INTO testname VALUES(%s,%s)''',(name,age))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Done!!"

@app.route('/createmovie', methods = ['POST', 'GET']) # HTML Form for post  # TODO
def createmovie():

    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':                # Title 	Year 	Director 	Genre 	Actors 	Poster 	imdbID 	
        Title = request.form['Title']
        Year = request.form['Year']
        Director = request.form['Director']
        Genre = request.form['Genre']
        Actors = request.form['Actors']
        Poster = request.form['Poster']
        imdbID = request.form['imdbID']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO movietable VALUES(%s,%s,%s,%s,%s,%s,%s)''',(Title,Year,Director,Genre,Actors,Poster,imdbID))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"                

@app.get('/api/v1/movies')  # Returns all rows in table movies 
def printresult():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT * FROM movies LIMIT 3 OFFSET 0"
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(results)
        return results
    cursor.close
    conn.close    




@app.get('/moviesuggestion')
def suggestion():
     conn = mysql.connect()
     cursor = conn.cursor(pymysql.cursors.DictCursor)
     query = " SELECT year,imdb_ID FROM movies LIMIT 3 OFFSET 0"          # Creates a copy of the original data table 
     cursor.execute(query)
     results = cursor.fetchall()
     for row in results:
        print(results)
        return results




     cursor.close
     conn.close    



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


@app.post("/api/v1/movies") # POST method for api/v1/movies there is a GET method on line 87
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

@app.route("/api/v1/testsearch")
def get_movie_from_omdb1():
    omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}" # /api/v1/search?title= <movie title here> returns all fields of data associated with OMDP APIS movie class  
    if "title" and "year" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"] + "&y=" + request.args["year"]).json()
    elif "title" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"]).json()
    return response

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
    return json.dumps(result)
        

@app.get("/api/v1/academy-awards/best-pictures/<int:year>")
def get_academy_awards_best_picture_winner(year: int):
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year and row[6] == "True" and (row[3] == "OUTSTANDING PICTURE" or row[3] == "BEST PICTURE"):
                movie_title = row[5]
    response = requests.get(omdb_url + "&t=" + movie_title).json()
    return response


@app.get("/api/v1/academy-awards/best-actors/<int:year>")
def get_academy_awards_best_actor_winner(year: int):
    with open(r"C:\Users\vcsa\Documents\GitHub\CSC131SoftWareProject\sachalDB\the_oscar_award.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if int(row[1]) == year and row[6] == "True" and row[3] == "ACTOR":
                movie_title = row[5]
    response = requests.get(omdb_url + "&t=" + movie_title).json()
    return response


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
