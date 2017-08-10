#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2017 Ivo Tzvetkov
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

from __future__ import print_function, unicode_literals, absolute_import
import sys
from redmsg import Subscriber
from .handlers.sqlalchemy import SQLAlchemyHandler

handlers = {
    'sqlalchemy': SQLAlchemyHandler
}

class Logger(object):

    def __init__(self, config):
        self.channel = config['channel']
        self.subscriber = Subscriber(**config['redmsg'])
        self.handler = handlers[config['handler']](config[config['handler']])

    def start(self):
        self.subscriber.subscribe(self.channel)
        latest_txid = self.handler.get_latest_txid(self.channel)
        generator = self.subscriber.listen() if latest_txid is None else \
                    self.subscriber.listen_from(latest_txid)
        for message in generator:
            try:
                self.handler.handle(message)
            except Exception as e:
                sys.stderr.write('{0}: {1}: {2}\n'.format(e.__class__.__name__, e, message).encode('utf-8'))

def main():
    import yaml
    from argparse import ArgumentParser
    arg_parser = ArgumentParser()
    arg_parser.description = 'RedMsg logging service.'
    arg_parser.add_argument('--config', metavar='FILE', default='config.yaml',
                            help='path to config file (default: %(default)s)')
    args = arg_parser.parse_args()

    with open(args.config, 'r') as file:
        config = yaml.load(file)

    logger = Logger(config)
    logger.start()

if __name__ == '__main__':
    main()
