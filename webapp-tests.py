#!/usr/bin/env python
# Fedora Hosted Processor - Tests
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

import os
import main
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
        root = self.app.get('/')
        assert 'Trac Instance?' in root.data

    def test_form_errors(self):
        post = self.app.post('/', data=dict(
                project_name="test",
                project_pretty_name="A test project",
                project_description="", # Should error.
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        assert 'Field must be between 1 and' in post.data

    def test_form_success(self):
        post = self.app.post('/', data=dict(
                project_name="test",
                project_pretty_name="A test project",
                project_description="This project does X and Y and Z too!",
                project_owner="testaccount",
                project_scm="git",
                project_trac=True), follow_redirects=True)
        assert 'Your request has been received.' in post.data

    def test_show_pending(self):
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

    def test_jsonify_invalid_id(self):
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

if __name__ == '__main__':
    unittest.main()
