#! /usr/bin/env python3
#
# Copyright (c) 2020 Gilles Chehade <gilles@poolp.org>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import io
import sys

try:
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    stdin = sys.stdin
    stdout = sys.stdout
except:
    stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def failure(token):
    stdout.write("table-result|%s|failure\n" % token)
    stdout.flush()

def updated(token):
    stdout.write("table-result|%s|updated\n" % token)
    stdout.flush()

def boolean(token, found):
    if not found:
        stdout.write("table-result|%s|not-found\n" % token)
    else:
        stdout.write("table-result|%s|found\n" % token)
    stdout.flush()

def result(token, result=None):
    if result is None:
        stdout.write("table-result|%s|not-found\n" % token)
    else:
        stdout.write("table-result|%s|found|%s\n" % (token, result))
    stdout.flush()        

updateCb = lambda x, y: updated(x)
checkCb = None
lookupCb = None
fetchCb = None

def on_update(cb):
    global updateCb
    updateCb = cb

def on_check(cb):
    global checkCb
    checkCb = cb

def on_lookup(cb):
    global lookupCb
    lookupCb = cb

def on_fetch(cb):
    global fetchCb
    fetchCb = cb

def dispatch():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()

        atoms = line.split('|')
        if len(atoms) < 6:
            sys.stderr.write("missing atoms: %s\n" % line)
            sys.exit(1)

        if atoms[0] != "table":
            sys.stderr.write("invalid stream: %s\n" % atoms[0])
            sys.exit(1)

        if atoms[1] != "0.1":
            sys.stderr.write("unsupported protocol version: %s\n" % atoms[1])
            sys.exit(1)

        table_name = atoms[3]
        token = atoms[5]
        if atoms[4] == "update":
            updateCb(token, table_name)
        elif atoms[4] == "check":
            checkCb(token, table_name, atoms[6], '|'.join(atoms[7:]))
        elif atoms[4] == "lookup":
            lookupCb(token, table_name, atoms[6], '|'.join(atoms[7:]))
        elif atoms[4] == "fetch":
            fetchCb(token, table_name, atoms[6])
        else:
            sys.stderr.write("unsupported operation: %s\n" % atoms[4])
            sys.exit(1)            

if __name__ == "__main__":
    dispatch()
