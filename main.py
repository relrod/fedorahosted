#!/usr/bin/env python
# Fedora Hosted Processor
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flaskext.flask_scss import Scss

DEBUG = True
SECRET_KEY = 'kF6BV5z6v5WVKmetjLhQqr2SffSKfrzFUaeIC19exox5b165ULsd7lR2Nb7q'

app = Flask(__name__)
app.config.from_object(__name__)
Scss(app)

@app.route("/")
def hello():
    return render_template('hello.html')

if __name__ == "__main__":
    app.run()
