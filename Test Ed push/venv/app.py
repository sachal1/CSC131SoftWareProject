# Test for add, commit and push
from flask import Flask

app = Flask(__name__)


@app.route('/')
def welcome():
    return 'Hello Team hope everyone is doing well and having a good one'
