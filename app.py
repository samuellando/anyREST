from flask import Flask
from anyrest import handlers

app = Flask(__name__)
app.register_blueprint(handlers.api)
