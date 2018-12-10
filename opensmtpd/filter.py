#! /usr/bin/env python3

import sys

class SMTP_IN(object):
    def __init__(self, logfile=None, event_log=None):
        self._report_callback = {}
        self._filter_callback = {}
        self._on_message = None
        self.event_log = open(event_log, "r") if event_log else sys.stdin
        self._logger = open(logfile, "w+") if logfile else None

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
            line = self.event_log.readline()
            if not line:
                break
            line = line.strip()
            if self._logger:
                self._logger.write(line + "\n")
                self._logger.flush()

            kind = line.split('|')[0]
            if kind == 'report':
                self._report(line)
            elif kind == 'filter':
                self._filter(line)


def proceed(session_id):
    sys.stdout.write("filter-result|%s|proceed\n" % (session_id, ))
    sys.stdout.flush()

def reject(session_id, reason):
    sys.stdout.write("filter-result|%s|reject|%s\n" % (session_id, reason))
    sys.stdout.flush()

def disconnect(session_id, reason):
    sys.stdout.write("filter-result|%s|disconnect|%s\n" % (session_id, reason))
    sys.stdout.flush()

def writeline(session_id, line):
    sys.stdout.write("filter-dataline|%s|%s\n" % (session_id, line))
    sys.stdout.flush()

"""
def link_connect(timestamp, session_id, args):
    rdns, fcrdns, laddr, raddr = args

def link_disconnect(timestamp, session_id, args):
    _ = args

def tx_begin(timestamp, session_id, args):
    tx_id = args[0]

def tx_mail(timestamp, session_id, args):
    tx_id, mail_from, status = args

def tx_rcpt(timestamp, session_id, args):
    tx_id, rcpt_to, status = args

def tx_envelope(timestamp, session_id, args):
    tx_id, evp_id = args
    
def tx_rollback(timestamp, session_id, args):
    tx_id = args[0]

def tx_commit(timestamp, session_id, args):
    tx_id, nbytes = args

def protocol_client(timestamp, session_id, args):
    line = args[0]
    
def protocol_server(timestamp, session_id, args):
    line = args[0]

def filter_connected(timestamp, session_id, args):
    #rdns, fcrdns, laddr, raddr = args
    rdns, laddr = args
    proceed(session_id)

def filter_helo(timestamp, session_id, args):
    hostname = args[0]
    proceed(session_id)

def filter_ehlo(timestamp, session_id, args):
    hostname = args[0]
    proceed(session_id)

def filter_mail_from(timestamp, session_id, args):
    mail_from = args[0]
    proceed(session_id)

def filter_rcpt_to(timestamp, session_id, args):
    rcpt_to = args[0]
    proceed(session_id)

def filter_data(timestamp, session_id, args):
    proceed(session_id)

def filter_data(timestamp, session_id, args):
    proceed(session_id)

def filter_rset(timestamp, session_id, args):
    proceed(session_id)

def filter_quit(timestamp, session_id, args):
    proceed(session_id)

def filter_commit(timestamp, session_id, args):
    proceed(session_id)

def filter_data_line(timestamp, session_id, args):
    line = args[0]
    writeline(session_id, line)
    

if __name__ == "__main__":
    o = SMTP_IN(logfile="/tmp/output.log")

    o.on_report('link-connect', link_connect)
    o.on_report('link-disconnect', link_disconnect)

    o.on_report('tx-begin', tx_begin)
    o.on_report('tx-mail', tx_mail)
    o.on_report('tx-rcpt', tx_rcpt)
    o.on_report('tx-envelope', tx_envelope)
    o.on_report('tx-commit', tx_commit)
    o.on_report('tx-rollback', tx_rollback)

    o.on_report('protocol-client', protocol_client)
    o.on_report('protocol-server', protocol_server)


    o.on_filter('connected', filter_connected)
    o.on_filter('helo', filter_helo)
    o.on_filter('ehlo', filter_ehlo)
    o.on_filter('mail-from', filter_mail_from)
    o.on_filter('rcpt-to', filter_rcpt_to)
    o.on_filter('data', filter_data)
    o.on_filter('rset', filter_rset)
    o.on_filter('quit', filter_quit)
    o.on_filter('commit', filter_commit)

    o.on_filter('data-line', filter_data_line)

    o.run()
"""
