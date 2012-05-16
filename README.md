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

# Dependencies (fedora packages)

* python-fedora
* python-flask
* python-flask-sqlalchemy
* python-flask-wtf

# Deploying

To set up the app, copy the included `fedorahosted_config.py.dist` to
`fedorahosted_config.py` and edit its values appropriately.

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

`pep8 *.py && python webapp-tests.py`

Above all, have fun!
  
# License

GPLv2+
