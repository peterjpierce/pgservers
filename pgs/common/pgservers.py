import logging
import os

import psutil

from pgs.common import errors

log = logging.getLogger(__name__)


class Servers:
    """Constellation of servers as defined in the instance map."""

    def __init__(self, instance_map):
        self.instance_map = instance_map
        self.servers = self._build_server_set(instance_map)
        self._cursor = 0

    @property
    def instance_names(self):
        """Get sorted list of instance names."""
        return sorted([s.name for s in self.servers])

    def get_instance(self, instance_name):
        """Retrieve a named instance from the set."""
        found = [s for s in self.servers if s.name == instance_name]

        if len(found) != 1:
            error_msg = 'invalid instance identifier: %s' % instance_name
            log.error(error_msg)
            raise errors.InvalidServerError(error_msg)

        return found[0]

    def _build_server_set(self, instance_map):
        """Construct the appropriate set of PGServer objects."""
        return [PGServer(instance, configs) for instance, configs in instance_map.items()]

    def __len__(self):
        return len(self.servers)

    def __iter__(self):
        return self

    def __next__(self):
        """Basic iterator to retrieve all servers."""
        if len(self.servers) > self._cursor:
            server = self.servers[self._cursor]
            self._cursor += 1
            return server
        else:
            raise StopIteration


class PGServer:

    def __init__(self, instance_identifier, configuration_directives):
        """Arg instance is the unique instance identifier."""
        self.cfg = configuration_directives
        self.name = instance_identifier

    @property
    def pidfile(self):
        """Dynamically refresh PID file state with each invocation."""
        return PIDFile(self.cfg['pgdata'])

    @property
    def process(self):
        """get a fresh Process corresponding to the latest PID file, if any."""
        return psutil.Process(self.pidfile.pid) if self.pidfile.pid else None

    @property
    def running(self):
        """Determine status of current process, based on postmaster.pid."""
        return bool(self.pidfile.pid and self.process.is_running())

    def start(self):
        """Start an instance."""
        if self.running:
            log.warn('%s is already running' % self.name)
        else:
            self._pg_ctl('start', log=self.cfg['log'])

    def stop(self):
        """Stop an instance."""
        if self.running:
            self._pg_ctl('stop')
        else:
            log.warn('%s is already stopped' % self.name)

    def status(self):
        """Get status for an instance."""
        if self.running:
            print('%s (%d) is running with %d child processes' % (
                self.name, self.process.pid, len(self.process.children())
            ))
        else:
            print('%s is not running' % self.name)

    def restart(self):
        """Restart an instance."""
        if self.running:
            self._pg_ctl('restart', log=self.cfg['log'])
        else:
            log.warn('%s is not running, just issuing start' % self.name)
            self.start()

    def reload(self):
        """Reload the configuration file for an instance."""
        self._pg_ctl('reload')

    def promote(self):
        """Promote an instance out of replication mode and allow writing."""
        self._pg_ctl('promote')

    def _pg_ctl(self, operation, *args, **kwargs):
        """Issue pg_ctl commands for a given operation and command line options.

        Argument args should be used for positionals like -W, and kwargs will
        be built in named values like --log="/var/log/blah".

        This always sets -D (--pgdata) so no need to pass that, and --silent.
        Returns the process ID.
        """
        cmd = [
            os.path.join(self.cfg['pgbinaries'], 'bin', 'pg_ctl'),
            operation,
            '--silent',
            '--pgdata=%s' % self.cfg['pgdata'],
        ]
        cmd.extend(args)

        for arg, val in kwargs.items():
            cmd.append('--%s="%s"' % (arg, val))

        pglib = os.path.join(self.cfg['pgbinaries'], 'lib')
        ldlib = os.environ['LD_LIBRARY_PATH']

        if pglib not in ldlib:
            log.debug('prepending %s to LD_LIBRARY_PATH for %s' % (pglib, self.name))
            os.environ['LD_LIBRARY_PATH'] = '%s:%s' % (pglib, ldlib)

        log.debug('issuing %s for instance %s' % (operation, self.name))
        log.debug('args are: %s' % str(cmd))
        return psutil.Popen(cmd)


class PIDFile:
    """Abstraction around and utilities for PID files."""

    def __init__(self, pgdata_dir):
        self.path = os.path.join(pgdata_dir, 'postmaster.pid')

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def pid(self):
        value = self._read_pidfile()
        if value:
            if psutil.pid_exists(value):
                return value
            else:
                log.warn('removing stale pidfile %s (%d)' % (self.basename, value))
                os.remove(self.path)
        return None

    def _read_pidfile(self):
        """Get the PID as an integer, or return None if no such file."""
        if not os.path.exists(self.path):
            return None
        try:
            with open(self.path, 'r') as f:
                return int(f.readline().strip())
        except IOError:
            raise
