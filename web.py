import os
from flask import Flask

app = Flask(__name__)

@app.route('/rsvp/')
def rsvp():
    return 'Hello World!'
