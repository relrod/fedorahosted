#!/usr/bin/env python
# Fedora Hosted Processor
# Ricky Elrod <codeblock@fedoraproject.org>
# GPLv2+

import argparse

parser = argparse.ArgumentParser(description='Fedora Hosted Request CLI')
parser.add_argument('-n', '--noop', action='store_true', help="Just print the commands that would be executed, don't actually execute them.")
parser.add_argument('-p', help='Process a Fedora Hosted request (run on fedorahosted.org server).')
parser.add_argument('-r', help='Request a new Fedora Hosted project.')
args = parser.parse_args()

