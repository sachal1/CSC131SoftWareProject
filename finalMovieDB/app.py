# import json

from flask import Flask
# from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
# from flask_sqlalchemy import SQLAlchemy
# import simplejson
# import requests
# import simplejson as json

# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
