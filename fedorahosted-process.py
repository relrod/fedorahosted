#!/usr/bin/env python
# Fedora Hosted Processor
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

import argparse
import urllib2
import json
import getpass
import socket
import sys
import os
import subprocess
import shlex

parser = argparse.ArgumentParser(description='Fedora Hosted Request CLI')
parser.add_argument('-n',
                    '--noop',
                    action='store_true',
                    help="Don't actually execute any commands.")
parser.add_argument('-v',
                    '--verbose',
                    action='store_true',
                    help="Be verbose, for debugging.")
parser.add_argument('-p',
                    '--process',
                    dest="REQUEST_ID",
                    help='Process a Fedora Hosted request (for admins).')
parser.add_argument('-r',
                    help='Request a new Fedora Hosted project.')
parser.add_argument('-s',
                    '--server',
                    dest="SERVER",
                    default="http://localhost:5000",
                    help='Server hosting the Fedora Hosted Request web app.')
args = parser.parse_args()


def run_command_if_allowed(command):
    """
    Runs a system command and prints the result.
    "allowed" is determined by the state of args.noop.
    """
    user = getpass.getuser()
    if user == "root":
        prompt = "#"
    else:
        prompt = "$"
    print "[%s@%s %s]%s %s" % (
        user,
        socket.gethostname(),
        os.getcwd(),
        prompt,
        command)
    if args.noop:
        return
    escaped = shlex.split(command)
    cmd = subprocess.Popen(escaped,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    if stdout:
        print "[stdout] %s" % stdout.strip()
    if stderr:
        print "[stderr] %s" % stderr.strip()


def verbose_print(text):
    """Prints a line if we are in verbose mode."""
    if args.verbose:
        print text

if args.noop:
    print
    print "*** Running in NO-OP mode, not executing any commands. ***"
    print "*** Not asking for FAS info, no FAS communication will happen. ***"
    print "If everything looks good below, run without -n/--noop"
    print

if args.REQUEST_ID:
    if not args.noop:
        processor_username = raw_input("FAS username: ")
        processor_password = getpass.getpass("FAS password: ")

    request = urllib2.urlopen(args.SERVER + '/getrequest?id=' +
                              args.REQUEST_ID)
    project = json.loads(request.read())

    verbose_print("Response from the webapp server: %s" % project)

    if 'error' in project:
        print "ERROR: %s" % project['error']
        sys.exit(1)

    project_group = str(project['scm'] + project['name'])

    # print "Creating FAS group: " + project_group
    # if not create_fas_group(project_group):
    #     print "ERROR creating FAS group: " + project['scm'] + project['name']
    #     sys.exit(1)

    # I wish Python had a switch/case equivalent.
    if project['scm'] == 'git':
        print "Creating /git/" + project['name'] + ".git directory."
        print "Entering /git/" + project['name'] + ".git directory."
        if not args.noop:
            os.mkdir("/git/" + project['name'] + ".git")
            os.chdir("/git/" + project['name'] + ".git")
            print "Working directory: " + os.getcwd()

        run_command_if_allowed("git --bare init --shared=true")

        print "Writing 'description' file."
        if not args.noop:
            with open("description", "w") as description:
                description.write(project['description'])

        print "Creating post-update symlink."
        if not args.noop:
            if os.path.isfile("hooks/post-update"):
                os.unlink("hooks/post-update")
            os.symlink(
                "/usr/share/git-core/templates/hooks/post-update.sample",
                "hooks/post-update")

        # TODO: Is it worth pythonizing these one day?
        run_command_if_allowed("git update-server-info")
        run_command_if_allowed("find -type d -exec chmod g+s {} ;")
        run_command_if_allowed(
            "find -perm /u+w -a ! -perm /g+w -exec chmod g+w {} ;")
        run_command_if_allowed(
            "chown -R " + str(project['owner']) + ":" + project_group + " .")

        # TODO: Mailing (and commit) lists.

    elif project['scm'] == 'hg':
        do_things()
    elif project['scm'] == 'svn':
        do_things()
