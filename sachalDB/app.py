from flask import Flask, flash, jsonify, request 
import requests
from flask import Flask,render_template, request
from flask_mysqldb import MySQL



app = Flask(__name__)
HOST = "localhost"
PORT = 5000
OMDB_API_KEY = "c37e6c14"



# MYSQL Connection procedure

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)


@app.route("/foo") # Test Endpoint 
def hello_world():
    return "Hello, World!"


#@app.route('/login', methods = ['POST', 'GET']) # connection tester - Tester for info_table DB - works 
#def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"


# Creates a movie table in database "flask" called "movietable"
@app.route("/create")
def create():
    cursor = mysql.connection.cursor()
    query=("CREATE TABLE movietable (Title VARCHAR(255),Year VARCHAR(255), Director VARCHAR(255), Genre VARCHAR(255), Actors VARCHAR(255), Poster VARCHAR(255), imdbID VARCHAR(255))")
    cursor.execute(query)
    mysql.connection.commit()
    cursor.close()
    return "table has been created"

@app.route('/form') # connection tester - Login form sent via HTML to login to MYSQL 
def form():
    return render_template('movie.html')

@app.route('/createmovie', methods = ['POST', 'GET']) # connection tester - Tester for info_table DB - works 
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




@app.route("/api/v1/search")
def get_movie_from_omdb():
    omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}" # /api/v1/search?title=
    if "title" and "year" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"] + "&y=" + request.args["year"]).json()
    elif "title" in request.args:
        response = requests.get(omdb_url + "&t=" + request.args["title"]).json()
    return response



#Creating a connection cursor
# cursor = mysql.connection.cursor()
 
#Executing SQL Statements ---- Cursor statements are very powerful it allows for database scans, executes SQL Queries and can even delete table record along with all other operations = CRUD 
# cursor.execute(''' CREATE TABLE table_name(field1, field2...) ''')
# cursor.execute(''' INSERT INTO table_name VALUES(v1,v2...) ''')
# cursor.execute(''' DELETE FROM table_name WHERE condition ''')
 
#Saving the Actions performed on the DB
# mysql.connection.commit() # Because MySQL is not an auto-commit DB, we must manually commit, i.e. save the changes/actions performed by the cursor execute on the DB.


 
#Closing the cursor
# cursor.close() 

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)


