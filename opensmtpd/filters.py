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
        self.stream = stream

    def on_report(self, event, func):
        self._report_callback[event] = func

    def on_filter(self, event, func):
        self._filter_callback[event] = func
    
    def _report(self, line):
        fields = line.split('|')
        _, _, timestamp, subsystem, event, session_id = fields[0:6]

        if event in self._report_callback:
            self._report_callback[event](timestamp, session_id, fields[6:])

    def _filter(self, line):
        fields = line.split('|')
        _, _, timestamp, subsystem, event, session_id = fields[0:6]
        
        if event in self._filter_callback:
            self._filter_callback[event](timestamp, session_id, fields[6:])
            return

        if event == 'data-line':
            out_line = '|'.join(fields[6:])
            sys.stdout.write("filter-dataline|%s|%s\n" % (session_id, out_line))
            sys.stdout.flush()
            return

        sys.stdout.write("filter-result|%s|proceed\n" % (session_id, ))
        sys.stdout.flush()
        
    def run(self):
        while True:
            line = self.stream.readline()
            if not line:
                break
            line = line.strip()
            kind = line.split('|')[0]
            if kind == 'report':
                self._report(line)
            elif kind == 'filter':
                self._filter(line)


