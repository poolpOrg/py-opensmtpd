#! /usr/bin/env python3
#
# Copyright (c) 2018 Gilles Chehade <gilles@poolp.org>
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


def proceed(token, session_id):
    stdout.write("filter-result|%s|%s|proceed\n" % (token, session_id))
    stdout.flush()

def rewrite(token, session_id, response):
    stdout.write("filter-result|%s|%s|rewrite|%s\n" % (token, session_id, response))
    stdout.flush()

def reject(token, session_id, reason):
    stdout.write("filter-result|%s|%s|reject|%s\n" % (token, session_id, reason))
    stdout.flush()

def disconnect(token, session_id, reason):
    stdout.write("filter-result|%s|%s|disconnect|%s\n" % (token, session_id, reason))
    stdout.flush()

def dataline(token, session_id, line, flush=True):
    stdout.write("filter-dataline|%s|%s|%s\n" % (token, session_id, line))
    if flush:
        stdout.flush()


class smtp_in(object):
    def __init__(self, stream = None):
        self._report_callback = {}
        self._filter_callback = {}
        self._event_callback = None
        self.istream = stream or stdin

    def on_report(self, event, func, arg):
        self._report_callback[event] = (func, arg)

    def on_filter(self, event, func, arg):
        self._filter_callback[event] = (func, arg)

    def on_event(self, func, arg):
        self._event_callback = (func, arg)

    def _register(self):
        if self._event_callback:
            stdout.write("register|report|smtp-in|*\n")
            stdout.flush()
        else:
            for key in self._report_callback:
                stdout.write("register|report|smtp-in|%s\n" % key)
            stdout.flush()

        if self._filter_callback:
            for key in self._filter_callback:
                stdout.write("register|filter|smtp-in|%s\n" % key)
            stdout.flush()
        stdout.write("register|ready\n")
        stdout.flush()

    def _report(self, timestamp, event, session_id, params):
        if event in self._report_callback:
            func, arg = self._report_callback[event]
            func(arg, timestamp, session_id, params)

    def _filter(self, timestamp, event, token, session_id, params):
        if event in self._filter_callback:
            func, arg = self._filter_callback[event]
            func(arg, timestamp, token, session_id, params)
            return

        if event == 'data-line':
            dataline(session_id, token, '|'.join(params[7:]))
            return

        proceed(session_id)

        
    def run(self):

        self._register()

        while True:
            line = self.istream.readline()
            if not line:
                break

            if self._event_callback:
                func, arg = self._event_callback
                func(arg, line.strip())

            fields = line.strip().split('|')
            kind, version, subsystem = fields[0], fields[1], fields[3]

            if subsystem != "smtp-in":
                continue

            if kind == 'report' and version == '1':
                kind, version, timestamp, subsystem, event, session_id = fields[0:6]
                params = fields[6:]
                self._report(timestamp, event, session_id, params)
            elif kind == 'filter' and version == '1':
                kind, version, timestamp, subsystem, event, token, session_id = fields[0:7]
                params = fields[7:]
                self._filter(timestamp, event, token, session_id, params)

            # either we received an unsupported message kind
            # or an unsupported message version, skip.
