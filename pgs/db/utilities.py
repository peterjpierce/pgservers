import csv
import io
import re

COLUMNS_PATTERN = '^\s*select\s+(\S.*?)\s+from.*'


def analyze_sql(sql):
    """Returns a tuple (is_select, fields, column_map) for a given SQL statement.

    Variable fields is a list of column names derived from the SQL if this
    is a SELECT statement, else an empty list is returned.

    Variable column_map is a [(0,f0), (1,f1),...] mapping of field positions,
    where the field names are lower-cased from fields.  This is a convenient
    construct for building dictionaries and Record objects.
    """

    def _get_tuple(source, delimiter=','):
        with io.StringIO(source.strip()) as f:
            reader = csv.reader(f, delimiter=delimiter, skipinitialspace=True)
            return [e for e in next(reader) if e]

    def _get_columns(source):
        """Read one or more columns in the SELECT part, seperated by commas."""
        return _get_tuple(source)

    def _get_column_parts(source):
        """Read elements of a column part."""
        return _get_tuple(source, delimiter=' ')

    fields = []
    sql_lines = re.split('\r?\n', sql, 0, re.S)
    sql = ' '.join(sql_lines)
    hit = re.match(COLUMNS_PATTERN, sql, re.I)
    is_select = bool(hit)

    if is_select:
        for column in _get_columns(hit.group(1)):
            words = _get_column_parts(column)
            if words and words[-1]:
                stripped = words[-1].split('.')[-1]
                fields.append(stripped)

    column_map = [(i, f.lower()) for (i,f) in enumerate(fields)]
    return (is_select, fields, column_map)
