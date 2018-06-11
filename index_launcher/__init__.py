#!/usr/bin/env python
# coding=utf-8
# Stan 2018-05-31

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)


import sys
import re
import json
import argparse
import codecs
import traceback
import logging
from importlib import import_module


__pkgname__ = __name__
__description__ = "A launcher for starting indexing of files"
__version__ = "0.1"


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3
if PY3:
    import configparser
else:
    import ConfigParser as configparser


def decode(code, value):
    if code == 'JSON':
        return json.loads(value)
    elif code == 'INT':
        return int(value)
    else:
        logging.warning(["Unknown code:", code])
        return value


def main(config=None):
    if not config:

        # argparse
        parser = argparse.ArgumentParser(prog='run_indexing.py',
                 description="A launcher for starting indexing of files")

        parser.add_argument('--version', action='version',
                            version='%(prog)s ver. {0}'.format(__version__),
                            help="show program's name and version number and exit")
        parser.add_argument('-v', action='version', version=__version__)
        parser.add_argument('-p', action='version', version=__pkgname__,
                            help="show package name and exit")
        parser.add_argument('-e', action='version', version=sys.version,
                            help="show python version and exit")

        parser.add_argument('config', nargs=1, help="specify config file",
                            metavar='file.cfg')

        if sys.version_info >= (3,):
            argv = sys.argv
        else:
            fse = sys.getfilesystemencoding()
            argv = [i.decode(fse) for i in sys.argv]

        args = parser.parse_args(argv[1:])

        config = args.config[0]

    # configparser
    c = configparser.ConfigParser()
    if PY3:
        c.read(config, encoding='utf8')
    else:
        with codecs.open(config, encoding="utf8") as f:
            c.readfp(f)

    if not c.has_section('launcher'):
        raise Exception("Unsupported config file or data not loaded!")

    # Check version
    ver = c.getint('launcher', 'ver')
    if ver != 1:
        raise Exception("Unsupported launcher version: {0}".format(ver))

    module = c.get('module', 'name')
    entry = c.get('module', 'entry')

    # Load module
    mod = import_module(module)

    # Load function, options and run
    func = getattr(mod, entry)
    options = dict(c.items('DEFAULT'))
    for key, value in options.items():
        res = re.split('^{{ (.+) }}', value, 1)
        if len(res) == 3:
            _, code, value = res
            options[key] = decode(code, value)

    if c.has_option('module', 'key'):
        key = c.get('module', 'key')
        return func(**{key: options})
    else:
        return func(options)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    er = main()

    if er is None:
        er = 0

    if isinstance(er, tuple):
        er, msg = er

    sys.exit(er)
