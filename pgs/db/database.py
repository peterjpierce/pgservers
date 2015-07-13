import logging
import re
import sqlalchemy
import sqlalchemy.orm

from pgs.common import errors, records
from pgs.db.utilities import analyze_sql

log = logging.getLogger(__name__)


class Database():
    """Provides database connection (to most types) and queries."""

    def __init__(self, sqlalchemy_url):
        self.session = self._open_session(sqlalchemy_url)

    def __del__(self):
        """Explicitly close an open database connection when destroyed."""
        try:
            self.session.close()
            log.debug('closed database connection')
        except AttributeError:
            pass

    def commit(self):
        """Commit a transaction."""
        log.debug('committing')
        self.session.commit()

    def rollback(self):
        """Roll back a transaction."""
        log.debug('rolling back')
        self.session.rollback()

    def query(self, sql, record_class=records.Record, logsql=True, **kwargs):
        """Execute a raw query and return the results.

        Does optional string interpolation on the SQL if kwargs provided.

        If a SELECT query, this returns a list of Record objects with fields
        named to match columns defined in the SELECT (lower cased).  Other
        query types return a scalar value (e.g., the number of rows affected).

        Note that you can optional specify a Record subclass instead.
        """
        sql = sql.format(**kwargs) if kwargs else sql
        sql = sql.strip()
        is_select, fields, column_map = analyze_sql(sql)
        result_set = []

        if logsql:
            log.debug('executing query:\n%s' % sql)

        try:
            rs = self.session.execute(sql)
        except Exception as err:
            log.exception(err)
            raise errors.DatabaseError(err)

        if is_select:
            for row in rs:
                rowdata = {}
                for idx, fld in column_map:
                    rowdata[fld] = row[idx]
                result_set.append(record_class(rowdata))
            return result_set
        elif re.search('^(update|delete)\s', sql, re.I):
            return rs.rowcount
        else:
            return None

    def _open_session(self, sqlalchemy_url):
        """Opens a connection and returns a SQLAlchemy session."""
        engine = sqlalchemy.create_engine(sqlalchemy_url)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        log.debug('opening database connection')
        new_session = Session()
        return new_session
