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
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)


@app.route("/foo") # Test Endpoint 
def hello_world():
    return "Hello, World!"

@app.route('/form') # connection tester - Login form sent via HTML to login to MYSQL 
def form():
    return render_template('form.html')

@app.route('/login', methods = ['POST', 'GET']) # connection tester - Tester for info_table DB - works 
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age)) # INSERT INTO - DB: flask > Table Name: info_table 
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"

@app.route("/")                     # sequence table endpoint used for auto incrementing through a db table and returning in numerical order from highest to lowest id (1,2,3 ....... ) DB: flask > Table Name: sequence 
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT DATA FROM sequence WHERE id = 1''')
    rv=cursor.fetchall()
    return str(rv)

@app.route('/increment/<string:insert>')
def add(insert):
    cursor = mysql.connection.cursor()





@app.route('getall')       # GET Route returner tester for info_table test db 
def getall():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM `info_table`''')
    returnvals = cursor.fetchall() # ((Name, Age ))

    printthis= ""
    for i in returnvals:
        printthis += i + "<br>"
    return printthis

@app.route("/api/v1/search")
def get_movie_from_omdb():
    omdb_url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}" # /api/v1/search?title= <movie title here> returns all fields of data associated with OMDP APIS movie class  
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


