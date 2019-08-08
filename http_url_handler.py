#! /usr/bin/env python3

import subprocess
import logging
import argparse
import syslog
import sys

try :
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import os.path

def http_url(url):
    if url.startswith('http://'):
        return url
    if url.startswith('https://'):
        return url
    else:
        syslog.syslog(syslog.LOG_ERR, sys.argv[0] + ": not an HTTP/HTTPS URL: '{}'".format(url))
        raise argparse.ArgumentTypeError(
            "not an HTTP/HTTPS URL: '{}'".format(url))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Handler for http/https URLs.'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='More verbose logging',
        dest="loglevel",
        default=logging.WARNING,
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        '-d',
        '--debug',
        help='Enable debugging logs',
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    parser.add_argument(
        'url',
        type=http_url,
        help="URL starting with 'http://' or 'https://'",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logging.debug("args.url = '{}'".format(args.url))
    parsed = urlparse(args.url)
    if parsed.hostname == 'askubuntu.com':
        browser = 'firefox'
    else:
        browser = 'chromium-browser'
    logging.info("browser = '{}'".format(browser))
    cmd = [browser, args.url]
    try :
        status = subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        syslog.syslog(syslog.LOG_ERR, sys.argv[0] + "could not open URL with browser '{}': {}".format(browser, args.url))
        raise
