# Fedora Hosted Processor

This application stores, manages, and processes Fedora Hosted requests.

# Project Goals

## Web Interface

* Provide an easy interface for any person to request a project on Fedora
  Hosted, and store the requests in a database.
* Be awesome. Don't suck.

## CLI Interface

* Allow administrators to easily process new hosted requests.
* Allow users to easily create hosted requests (alternative to the web interface).
* Provide a noop mode to see what would happen without actually doing anything.
* Be awesome. Don't suck.

### Workflow

* Admin starts processing the request (`./fedorahosted-process.py -p 1`)
* Script asks for admin's FAS username/password.
* Script creates the new FAS group.
* Script runs all the commands needed on hostedXX.
* Script tells the web app to check with FAS and see if the new group exists.
  * This prevents having to send FAS auth info to the web app.
  * If the group exists, the web app sets HostedRequest.completed = true

# Dependencies (Fedora packages)

* python-fedora
* python-flask
* python-flask-sqlalchemy
* python-flask-wtf
* python-sqlalchemy
* python-wtforms
* python-argparse (for CLI, and only for Python <2.7 (needed on RHEL 6))
* python-pep8 (if you plan on hacking, not needed to deploy)

# Deploying

To set up the app, copy the included `etc/fedorahosted_config.py.dist` to
`etc/fedorahosted_config.py` and edit its values appropriately.

Then point the FEDORAHOSTED_CONFIG environment variable to this config:
``export FEDORAHOSTED_CONFIG=`pwd`/etc/fedorahosted_config.py``

If you're deploying via (the currently non-existent) rpm file, simply edit
`/etc/fedorahosted/flask_config.py` and:
`export FEDORAHOSTED_CONFIG=/etc/fedorahosted/flask_config.py`

Then, look to [Flask's Documentation](http://flask.pocoo.org/docs/deploying/)
for figuring out the best way to deploy. In Fedora Infrastructure, we will
likely use mod_wsgi, simply for the fact that we already have infrastructure
built up around it, and know how to support it.

# Hacking/Contributing

Please have read and signed the
[Fedora Project Contributor Agreement](http://da.gd/fpca) before sending
patches.

Please follow PEP 8 and ensure all unit tests pass.

A good `.git/hooks/pre-commit` hook is as follows (and make sure the hook is
chmod +x) though it does depend on the package: `python-pep8`:

`find . -type d -name fenv -prune -o -name '*.py' -print | xargs pep8 && python webapp-tests.py`

If you plan on contributing often, consider adding `FEDORAHOSTED_CONFIG` to
your .bash_profile. To do this, simply run this command, from the
**root directory** of your clone clone of the git repo. This prevents you from
having to export the variable every time you open a new shell and decide to
hack on the app.

``echo "export FEDORAHOSTED_CONFIG=`pwd`/etc/fedorahosted_config.py" >> ~/.bash_profile``

Above all, have fun, and don't be afraid to ask for help. We hang out in
\#fedora-apps on Freenode.

# License

GPLv2+
