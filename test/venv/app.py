from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def welcome():
    return 'Hello World!!!'
