#!/usr/bin/env python
# Fedora Hosted Processor
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify
from flaskext.flask_scss import Scss
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, TextField, SelectField, validators

DEBUG = True
SECRET_KEY = 'kF6BV5z6v5WVKmetjLhQqr2SffSKfrzFUaeIC19exox5b165ULsd7lR2Nb7q'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

app = Flask(__name__)
app.config.from_object(__name__)
Scss(app)
db = SQLAlchemy(app)

# TODO: Move these out to their own file.
class MailingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: What is the max length of ml title in mailman?
    name = db.Column(db.String(150), unique=True)
    request_id = db.Column(db.Integer, db.ForeignKey('hosted_request.id'))
    # TODO: wtf does this actually do?
    request = db.relationship('HostedRequest',
                              backref=db.backref('mailing_lists',
                                                 lazy='dynamic'))

class HostedRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    pretty_name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(255))
    scm = db.Column(db.String(10))
    trac = db.Column(db.Boolean)
    owner = db.Column(db.String(32)) # 32 is the max username length in FAS
    completed = db.Column(db.Boolean, default=False)

class RequestForm(Form):
    project_name = TextField('Name (lowercase, alphanumeric only)',
                             [validators.Length(min=1, max=150)])
    project_pretty_name = TextField('Pretty Name',
                                    [validators.Length(min=1, max=150)])
    project_description = TextField('Short Description',
                            [validators.Length(min=1, max=255)])
    project_owner = TextField('Owner FAS Username',
                              [validators.Length(min=1, max=32)])
    project_scm = SelectField('SCM',
                      choices=[('git', 'git'), ('svn', 'svn'), ('hg', 'hg')])
    project_trac = BooleanField('Trac Instance?')
    # TODO: Handle mailing lists

@app.route('/', methods=['POST', 'GET'])
def hello():
    form = RequestForm(request.form)
    if request.method == 'POST' and form.validate():
        hosted_request = HostedRequest(
            name = form.project_name.data,
            pretty_name = form.project_pretty_name.data,
            description = form.project_description.data,
            scm = form.project_scm.data,
            trac = form.project_trac.data,
            owner = form.project_owner.data)
        db.session.add(hosted_request)
        db.session.commit()
        return render_template('completed.html')
    return render_template('hello.html', form=form)

@app.route('/pending')
def pending():
    requests = HostedRequest.query.filter_by(completed=False)
    return render_template('pending.html', requests=requests)

@app.route('/getrequest')
def get_request():
    """Returns a JSON representation of a Fedora Hosted Request."""
    hosted_request = HostedRequest.query.filter_by(id=request.args.get('id'))
    if hosted_request.count() > 0:
        d = {}
        for col in hosted_request[0].__table__.columns.keys():
            d[col] = getattr(hosted_request[0], col)
        return jsonify(d)
    else:
        return jsonify(error="No hosted request with that ID could be found.")

if __name__ == "__main__":
    app.run()
