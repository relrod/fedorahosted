#!/usr/bin/env python
# Fedora Hosted Processor
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

import argparse
import urllib2
import json
import getpass

parser = argparse.ArgumentParser(description='Fedora Hosted Request CLI')
parser.add_argument('-n',
                    '--noop',
                    action='store_true',
                    help="Don't actually execute any commands.")
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

if args.noop:
    print
    print "*** Running in NO-OP mode, not executing any commands. ***"
    print "If everything looks good below, run without -n/--noop"
    print

if args.REQUEST_ID:
    processor_username = raw_input("FAS username: ")
    processor_password = getpass.getpass("FAS password: ")
    request = urllib2.urlopen(args.SERVER + '/getrequest?id=' + args.REQUEST_ID)
    request_json = json.loads(request.read())
    print request_json
