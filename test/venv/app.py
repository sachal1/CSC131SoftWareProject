from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

HOST = "127.0.0.1"
PORT = 8080


engine = create_engine('mysql+pymysql://root:123456@127.0.0.1/movie_db')


@app.route("/hello-world")
def hello_world():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
