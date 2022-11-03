import pymysql
from app import app
from config import mysql
from flask import jsonify
from flask import flash, request
import requests

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


@app.post('/api/v1/create')
def create_emp():
    try:        
        _json = request.json
        _title = _json['title']
        _year = _json['year']
        _director = _json['director']
        _language = _json['language']	
        if _title and _year and _director and _language and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)		
            sqlQuery = "INSERT INTO emp(title, year, director, language) VALUES(%s, %s, %s, %s)"
            bindData = (_title, _year, _director, _language)            
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            respone = jsonify('Movie added successfully!')
            respone.status_code = 200
            return respone
        else:
            return showMessage()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()          


@app.route('/emp')
def emp():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, title, year, director, language FROM emp")
        empRows = cursor.fetchall()
        respone = jsonify(empRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close() 


@app.route('/emp/')
def emp_details(emp_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, title, year, director, language FROM emp WHERE id =%s", emp_id)
        empRow = cursor.fetchone()
        respone = jsonify(empRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close() 


@app.put('/update')
def update_emp():
    try:
        _json = request.json
        _id = _json['id']
        _title = _json['title']
        _year = _json['year']
        _director = _json['director']
        _language = _json['language']
        if _title and _year and _director and _language and _id and request.method == 'PUT':			
            sqlQuery = "UPDATE emp SET title=%s, year=%s, director=%s, language=%s WHERE id=%s"
            bindData = (_title, _year, _director, _language, _id,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            respone = jsonify('Movie updated successfully!')
            respone.status_code = 200
            return respone
        else:
            return showMessage()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close() 
        

@app.delete('/delete/')
def delete_emp(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM emp WHERE id =%s", (id,))
		conn.commit()
		respone = jsonify('Movie deleted successfully!')
		respone.status_code = 200
		return respone
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()


@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Movie was not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
