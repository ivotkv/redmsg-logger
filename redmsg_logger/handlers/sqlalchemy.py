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
import json
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from .base import BaseHandler
from .exc import HandlerException

class InvalidTableName(HandlerException):
    pass

class TableNotFound(HandlerException):
    pass

class SQLAlchemyDatabase(object):

    def __init__(self, config):
        self.url = '{0}://{1}:{2}@{3}/{4}'.format(config['type'],
                                                  config['user'],
                                                  config['pass'],
                                                  config['host'],
                                                  config['database'])
        self.engine = create_engine(self.url, pool_recycle=3600)
        self.automap = automap_base()
        self.automap.prepare(self.engine, schema=config['schema'], reflect=True)
        self.sessionmaker = sessionmaker(bind=self.engine, autoflush=False)

    def session(self):
        return self.sessionmaker()

    def table(self, name):
        table = getattr(self.automap.classes, name.lower(), None)
        if table is None:
            raise TableNotFound('table does not exist or is not a viable SQLAlchemy table: {0}'.format(name))
        elif not isinstance(table, DeclarativeMeta):
            raise InvalidTableName('reserved name cannot be a table name: {0}'.format(name))
        return table

class SQLAlchemyHandler(BaseHandler):

    def __init__(self, config):
        self.database = SQLAlchemyDatabase(config)

    def get_latest_txid(self):
        return None # TODO

    def handle(self, message):
        session = self.database.session()

        try:
            table = self.database.table(message['channel'])
            data = json.loads(message['data'])
            data['txid'] = message['txid']
            session.add(table(**data['data']))
        except Exception as e:
            error = self.database.table('logger_errors')
            if error is not None:
                entry = session.add(error(date=str(datetime.now()),
                                          error=e.__class__.__name__,
                                          description=str(e),
                                          channel=message['channel'],
                                          txid=message['txid'],
                                          data=message['data']))
            else:
                raise e

        session.commit()
