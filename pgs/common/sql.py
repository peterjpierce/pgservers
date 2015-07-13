VIABLE_DATABASES = """
    select
      d.datname db_name,
      u.usename db_owner
    from
      pg_database d
      left outer join pg_user u on (d.datdba = u.usesysid)
    where
      datistemplate = 'f' and
      datallowconn = 't' and
      datname <> 'postgres'
"""
