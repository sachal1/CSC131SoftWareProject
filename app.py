#

from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

HOST = "127.0.0.1"
PORT = 8080


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
