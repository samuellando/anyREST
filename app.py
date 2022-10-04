from flask import Flask
from anyrest.handlers import api

app = Flask(__name__)
app.register_blueprint(api)
