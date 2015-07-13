# pgservers

A framework for operating PostgreSQL servers, which provides:

+ A unified way to run one or many [PostgreSQL](http://www.postgresql.org) instances concurrently
+ Flexibility to simultaneously use any number of PostgreSQL versions
+ Succinct commands, consistent operations
+ The ability to start/stop/restart/reload/promote/status one, multiple or all servers at once
+ Simple configuration
+ Logging for history and troubleshooting

## Installation

**pgservers** has been tested on Linux and OS X.  It requires Python and some common libraries.

### Step 0: PostgreSQL instances and databases

These instructions assume you have followed the [PostgreSQL documentation](http://www.postgresql.org/docs/)
to:

+ install [server binaries](http://www.postgresql.org/download/)
+ initialize, configure and secure your databases
+ perform other routine DBA/network setup tasks

Note that you may host and run multiple PostgreSQL versions in parallel if you install
their binaries by building from source or using official distribution tarballs, because
these methods allow you to control installation locations.  For example, you might use
`/opt/pg/9.4.3` and `/opt/pg/9.1.18` to host two versions per the 
[FHS](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard). 

### Step 1: Install pgservers

Untar this project into the directory of your choice, such as `/opt/pgservers`. Filesystem
objects should be owned by the user that will be running your PostgreSQL servers.
This is often **postgres**.

Good practice suggests you set up a dedicated [Python virtual environment](https://docs.python.org/3/library/venv.html).
Many teams will create this enviroment under an `env/` sub-directory at the top of your
newly untarred project directory.  When ready, you can install the dependencies using
`pip install -r _setup/requirements.txt`

### Step 2: Configure pgservers

Edit pgserver's `etc/instances.yml` for each instance you will be running.
An example is provided, that looks like this:

```
pg1:
  pgdata: /var/local/data/pg/pg1
  pgport: 5512
  binaries: /opt/pg/servers/9.3.5
  log: /var/log/pg/pg1.log
  dba_connection:
    host: localhost
    username: postgres
    password: xxyyZZ3!

```

Where the values mean:

| Key          | Value |
| ------------ | -------- |
| `pg1       ` | server instance name |
| `pgdata    ` | database directory |
| `pgport    ` | port this instance listens on, must match `$PGDATA/postgresql.conf` |
| `binaries` | base directory for this instance's server binaries |
| `log       ` | full path to the desired PostgreSQL server log |
| `dba_connection` | database superuser login credentials |
 
You should not have to edit `etc/config.py` or `etc/log.py`.

## Running pgservers

File `bin/pgs` is the script to run (from within your virtualenv).
Use --help to see its instructions:

```
usage: pgs [-h] [-v] [-q] operation [instances [instances ...]]

Perform start/stop/status/etc. operations for PostgreSQL servers

positional arguments:
  operation      one of: start|stop|restart|reload|promote|status
  instances      instance list, or "all" (optional for status)

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  show debug logging on console
  -q, --quiet    suppress non-error logging on console

```

Supported operations include:

+ start
+ stop
+ restart
+ reload
+ promote
+ status

You may use the word `all` as an instance argument to task every instance at once
(`status` does not require an instance arg).

The log for **pgservers** is located in its `var/log/` subdirectory.

## Feedback
Please ask any questions, report problems, and provide feedback to:  peterjpierce@gmail.com

Thank you!
