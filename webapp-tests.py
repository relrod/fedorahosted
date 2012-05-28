#!/usr/bin/env python
# Fedora Hosted Processor - Tests
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

import os
from fedorahosted import main
import unittest
import tempfile
import json


class FedoraHostedTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.sqlite_tmp = tempfile.mkstemp()
        main.app.config['SQLALCHEMY_DATABASE_URI'] = \
            'sqlite:///' + self.sqlite_tmp
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()
        main.db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.sqlite_tmp)

    def test_form_displays(self):
        """Checks that the form on / displays."""
        root = self.app.get('/')
        assert 'Trac Instance?' in root.data

    def test_form_errors(self):
        """Checks that the form errors when it should"""
        post = self.app.post('/', data=dict(
                project_name="test",
                project_pretty_name="A test project",
                project_description="",  # Should error.
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        assert 'Field must be between 1 and' in post.data

    def test_form_success(self):
        """Checks that requests can be made successfully."""
        post = self.app.post('/', data=dict(
                project_name="test",
                project_pretty_name="A test project",
                project_description="This project does X and Y and Z too!",
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        assert 'Your request has been received.' in post.data

    def test_show_pending(self):
        """Checks that a list of pending requests can be generated."""
        self.app.post('/', data=dict(
                project_name="test",
                project_pretty_name="A test project",
                project_description="This project does X and Y and Z too!",
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        pending = self.app.get('/pending')
        assert 'A test project' in pending.data

    def test_jsonify_existing(self):
        """Checks that JSONifying existing requests works."""
        self.app.post('/', data=dict(
                project_name="test",
                project_pretty_name="A test project",
                project_description="This project does X and Y and Z too!",
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        hosting_request = self.app.get('/getrequest?id=1')
        okay = False
        try:
            # Can we load it, and without an 'error' key?
            parsed_json = json.loads(hosting_request.data)
            if 'error' not in parsed_json.keys():
                okay = True
        except ValueError, e:
            print str(e)
        assert okay

    def test_jsonify_mailing_list(self):
        """Checks that JSONifying works with a mailing list."""
        self.app.post('/', data={
                "project_name": "test",
                "project_pretty_name": "A test project",
                "project_description": "This project does X and Y and Z too!",
                "project_owner": "testaccount",
                "project_scm": "git",
                "project_trac": True,
                "project_mailing_lists-0": "test-list",
        }, follow_redirects=True)
        hosting_request = self.app.get('/getrequest?id=1')

        parsed_json = json.loads(hosting_request.data)

        self.assertEqual(len(parsed_json['list_request']), 1,
                         "Did mailing list make it and get jsonified back?")
        self.assertIn('commit_list', parsed_json['list_request'][0],
                      "Does the mailing list entry have a commit bool?")
        commit_list = parsed_json['list_request'][0]['commit_list']
        self.assertEqual(type(commit_list), bool,
                         "Is 'commit_list' a bool?")

    def test_require_valid_mailing_list_name(self):
        """Checks that a valid mailing list name is required."""
        response = self.app.post('/', data={
                "project_name": "test",
                "project_pretty_name": "A test project",
                "project_description": "This project does X and Y and Z too!",
                "project_owner": "testaccount",
                "project_scm": "git",
                "project_trac": True,
                "project_mailing_lists-0": "notatest-list",
        }, follow_redirects=True)

        self.assertRegexpMatches(response.data,
                                 "Mailing lists must start with the project" \
                                     " name")

        response = self.app.post('/', data={
                "project_name": "test",
                "project_pretty_name": "A test project",
                "project_description": "This project does X and Y and Z too!",
                "project_owner": "testaccount",
                "project_scm": "git",
                "project_trac": True,
                "project_mailing_lists-0": "test-list",
                "project_mailing_lists-1": "notatest-list",
        }, follow_redirects=True)

        self.assertRegexpMatches(response.data,
                                 "Mailing lists must start with the project" \
                                     " name")

        response = self.app.post('/', data={
                "project_name": "test",
                "project_pretty_name": "A test project",
                "project_description": "This project does X and Y and Z too!",
                "project_owner": "testaccount",
                "project_scm": "git",
                "project_trac": True,
                "project_mailing_lists-0": "test-list",
                "project_mailing_lists-1": "test-foo",
        }, follow_redirects=True)

        self.assertRegexpMatches(response.data,
                                 "Your request has been received")

    def test_jsonify_invalid_id(self):
        """Checks that we properly handle JSONifying a nonexistent request."""
        hosting_request = self.app.get('/getrequest?id=1337')
        okay = False
        try:
            # It should be parsable and have and 'error' key.
            parsed_json = json.loads(hosting_request.data)
            if 'error' in parsed_json.keys():
                okay = True
        except ValueError, e:
            print str(e)
        assert okay

    def test_mark_completed(self):
        """
        Checks that we can mark completed a hosted request, if a FAS group
        exists.
        """
        self.app.post('/', data=dict(
                project_name="testproject",
                project_pretty_name="A test project",
                project_description="This project does X and Y and Z too!",
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        completed = self.app.get('/mark-completed?group=gittestproject&id=1')
        parsed_json = json.loads(completed.data)
        assert parsed_json['success'] == "Request marked as completed."

    def test_already_marked_completed(self):
        """Checks that we properly handle already-completed requests."""
        self.app.post('/', data=dict(
                project_name="testproject",
                project_pretty_name="A test project",
                project_description="This project does X and Y and Z too!",
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        completed = self.app.get('/mark-completed?id=1')
        completed2 = self.app.get('/mark-completed?id=1')
        parsed_json = json.loads(completed2.data)
        assert parsed_json['error'] == \
            "Request was already marked as completed."

    def test_mark_completed_invalid_id(self):
        """
        Checks that we properly handle giving /mark-completed an invalid ID.
        """
        test_url = '/mark-completed?id=1234'
        completed = self.app.get(test_url)
        parsed_json = json.loads(completed.data)
        assert parsed_json['error'] == \
            "No hosted request with that ID could be found."


if __name__ == '__main__':
    unittest.main()
