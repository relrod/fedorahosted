#!/usr/bin/env python
# Fedora Hosted Processor
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import RelationshipProperty
from flaskext.wtf import Form, BooleanField, TextField, SelectField, \
    validators, FieldList, ValidationError
import fedora.client

app = Flask(__name__)

# Handle fedorahosted.main being imported (e.g. by webapp-tests.py)
# or not.
try:
    app.config.from_object('fedorahosted.default_config')
except ImportError:
    try:
        app.config.from_object('default_config')
    except ImportError:
        raise

app.config.from_envvar('FEDORAHOSTED_CONFIG')
db = SQLAlchemy(app)


class JSONifiable(object):
    """ A mixin for sqlalchemy models providing a .__json__ method. """

    def __json__(self, seen=None):
        """ Returns a dict representation of the object.

        Recursively evaluates .__json__() on its relationships.
        """

        if not seen:
            seen = []

        properties = list(class_mapper(type(self)).iterate_properties)
        relationships = [
            p.key for p in properties if type(p) is RelationshipProperty
        ]
        attrs = [
            p.key for p in properties if p.key not in relationships
        ]

        d = dict([(attr, getattr(self, attr)) for attr in attrs])

        for attr in relationships:
            d[attr] = self._expand(getattr(self, attr), seen)

        return d

    def _expand(self, relation, seen):
        """ Return the __json__() or id of a sqlalchemy relationship. """

        if hasattr(relation, 'all'):
            relation = relation.all()

        if hasattr(relation, '__iter__'):
            return [self._expand(item, seen) for item in relation]

        if type(relation) not in seen:
            return relation.__json__(seen + [type(self)])
        else:
            return relation.id


# TODO: Move these out to their own file.
class MailingList(db.Model, JSONifiable):
    id = db.Column(db.Integer, primary_key=True)
    # mailman does not enforce a hard limit. SMTP specifies 64-char limit
    # on local-part, so use that.
    name = db.Column(db.String, unique=True)

    @classmethod
    def find_or_create_by_name(self, name):
        """
        If a list with the given name exists, return it.
        Otherwise create it, *then* return it.
        """
        lists = self.query.filter_by(name=name)
        if lists.count() > 0:
            return lists.first()
        else:
            new_list = self(name=name)
            db.session.add(new_list)
            db.session.commit()
            return new_list


class ListRequest(db.Model, JSONifiable):
    id = db.Column(db.Integer, primary_key=True)
    commit_list = db.Column(db.Boolean, default=False)

    mailing_list_id = db.Column(db.Integer,
                                db.ForeignKey('mailing_list.id'))
    mailing_list = db.relationship('MailingList',
                                   backref=db.backref(
                                       'list_request', lazy='dynamic'))

    hosted_request_id = db.Column(db.Integer,
                                  db.ForeignKey('hosted_request.id'))
    hosted_request = db.relationship('HostedRequest',
                                     backref=db.backref(
                                         'list_request', lazy='dynamic'))


class HostedRequest(db.Model, JSONifiable):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    pretty_name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(255))
    scm = db.Column(db.String(10))
    trac = db.Column(db.Boolean)
    owner = db.Column(db.String(32))  # 32 is the max username length in FAS
    completed = db.Column(db.Boolean, default=False)
    mailing_lists = db.relationship('MailingList',
                                    secondary=ListRequest.__table__,
                                    backref=db.backref('hosted_requests',
                                                       lazy='dynamic'))


def valid_mailing_list_name(form, mailing_list):
    if not mailing_list.data:
        return
    if not mailing_list.data.startswith(form.project_name.data + '-'):
        raise ValidationError("Mailing lists must start with the project " \
                                  "name and a dash, e.g. '%s-users'" % (
                form.project_name.data))


def valid_email_address(form, commit_list):
    if not commit_list.data:
        return
    if not '@' in commit_list.data:
        raise ValidationError("Commit list must be a full email-address " \
                                  "(e.g. contain a '@' sign).")


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
                              choices=[('git', 'git'),
                                       ('svn', 'svn'),
                                       ('hg', 'hg')])
    project_trac = BooleanField('Trac Instance?')
    project_mailing_lists = FieldList(
        TextField('Mailing List (must start with the project name)',
                  [validators.Length(max=64), valid_mailing_list_name]),
        min_entries=1)
    project_commit_lists = FieldList(
        TextField('Send commit emails to (full email address)',
                  [valid_email_address]),
        min_entries=1)


@app.route('/', methods=['POST', 'GET'])
def hello():
    form = RequestForm()
    if form.validate_on_submit():
        # The hosted request itself (no mailing lists)
        hosted_request = HostedRequest(
            name=form.project_name.data,
            pretty_name=form.project_pretty_name.data,
            description=form.project_description.data,
            scm=form.project_scm.data,
            trac=form.project_trac.data,
            owner=form.project_owner.data)
        db.session.add(hosted_request)
        db.session.commit()

        # Mailing lists
        for entry in form.project_mailing_lists.entries:
            if entry.data:
                # The field wasn't left blank...
                list_name = entry.data

                # The person only entered the list name, not the full address.
                if not list_name.endswith("@lists.fedorahosted.org"):
                    list_name = list_name + "@lists.fedorahosted.org"

                mailing_list = MailingList.find_or_create_by_name(list_name)

                # The last step before storing the list is handling
                # commit lists -- lists that get commit messages -- which also
                # appear as regular lists.
                commit_list = False
                if list_name in form.project_commit_lists.entries:
                    del form.project_commit_lists.entries[list_name]
                    commit_list = True

                # Now we have a mailing list object (in mailing_list), we can
                # store the relationship using it.
                list_request = ListRequest(
                    mailing_list=mailing_list,
                    hosted_request=hosted_request,
                    commit_list=commit_list)
                db.session.add(list_request)
                db.session.commit()

        # Add the remaining commit list entries to the project.
        for entry in form.project_commit_lists.entries:
            if entry.data:
                mailing_list = MailingList.find_or_create_by_name(entry.data)
                list_request = ListRequest(
                    mailing_list=mailing_list,
                    hosted_request=hosted_request,
                    commit_list=True)
                db.session.add(list_request)
                db.session.commit()

        return render_template('completed.html')

    # GET, not POST.
    return render_template('index.html', form=form)


@app.route('/pending')
def pending():
    requests = HostedRequest.query.filter_by(completed=False)
    return render_template('pending.html', requests=requests)


@app.route('/getrequest')
def get_request():
    """Returns a JSON representation of a Fedora Hosted Request."""
    hosted_request = HostedRequest.query.filter_by(id=request.args.get('id'))
    if hosted_request.count() > 0:
        request_json = hosted_request.first().__json__()
        del request_json['mailing_lists']
        return jsonify(request_json)
    else:
        return jsonify(error="No hosted request with that ID could be found.")


@app.route('/mark-completed')
def mark_complete():
    """
    Checks to see if a group exists in FAS for the given project and marks the
    project complete if it does. We do this this way so that we don't have to
    send FAS credentials to this app.
    """
    fas = fedora.client.AccountSystem(username=app.config['FAS_USERNAME'],
                                      password=app.config['FAS_PASSWORD'])
    hosted_request = HostedRequest.query.filter_by(id=request.args.get('id'))
    if hosted_request.count() > 0:
        if hosted_request[0].completed == True:
            return jsonify(error="Request was already marked as completed.")

        group_name = hosted_request[0].scm + hosted_request[0].name
        try:
            group = fas.group_by_name(group_name)
        except:
            return jsonify(error="No such group: " + group_name)

        hosted_request[0].completed = True
        db.session.commit()
        return jsonify(success="Request marked as completed.")
    else:
        return jsonify(error="No hosted request with that ID could be found.")

if __name__ == "__main__":
    app.run(host='127.0.0.1')
