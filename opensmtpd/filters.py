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

import sys


def proceed(session_id):
    sys.stdout.write("filter-result|%s|proceed\n" % session_id)
    sys.stdout.flush()

def rewrite(session_id, response):
    sys.stdout.write("filter-result|%s|rewrite|response\n" % (session_id, response))
    sys.stdout.flush()

def reject(session_id, reason):
    sys.stdout.write("filter-result|%s|reject|%s\n" % (session_id, reason))
    sys.stdout.flush()

def disconnect(session_id, reason):
    sys.stdout.write("filter-result|%s|disconnect|%s\n" % (session_id, reason))
    sys.stdout.flush()

def dataline(session_id, line, flush=True):
    sys.stdout.write("filter-dataline|%s|%s\n" % (session_id, line))
    if flush:
        sys.stdout.flush()


class smtp_in(object):
    def __init__(self, stream = sys.stdin):
        self._report_callback = {}
        self._filter_callback = {}
        self._event_callback = None
        self.stream = stream

    def on_report(self, event, func, arg):
        self._report_callback[event] = (func, arg)

    def on_filter(self, event, func, arg):
        self._filter_callback[event] = (func, arg)

    def on_event(self, func, arg):
        self._event_callback = (func, arg)

    def _register(self):
        if self._event_callback:
            sys.stdout.write("register|report|smtp-in|*\n")
            sys.stdout.flush()
        else:
            for key in self._report_callback:
                sys.stdout.write("register|report|smtp-in|%s\n" % key)
            sys.stdout.flush()

        if self._filter_callback:
            for key in self._filter_callback:
                sys.stdout.write("register|filter|smtp-in|%s\n" % key)
            sys.stdout.flush()
        sys.stdout.write("register|ready\n")
        sys.stdout.flush()

    def _report(self, timestamp, event, session_id, params):
        if event in self._report_callback:
            func, arg = self._report_callback[event]
            func(arg, timestamp, session_id, params)

    def _filter(self, timestamp, event, session_id, params):
        if event in self._filter_callback:
            func, arg = self._filter_callback[event]
            func(arg, timestamp, session_id, params)
            return

        if event == 'data-line':
            dataline(session_id, '|'.join(params[6:]))
            return

        proceed(session_id)

        
    def run(self):

        self._register()

        while True:
            line = self.stream.readline()
            if not line:
                break

            if self._event_callback:
                func, arg = self._event_callback
                func(arg, line.strip())

            fields = line.strip().split('|')
            kind, version, timestamp, subsystem, event, session_id = fields[0:6]
            params = fields[6:]

            if subsystem != "smtp-in":
                continue

            if kind == 'report' and version == '1':
                self._report(timestamp, event, session_id, params)
            elif kind == 'filter' and version == '1':
                self._filter(timestamp, event, session_id, params)

            # either we received an unsupported message kind
            # or an unsupported message version, skip.
