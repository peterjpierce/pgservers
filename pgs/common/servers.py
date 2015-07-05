import logging
import os
import time

import psutil

from pgs.common import errors

log = logging.getLogger(__name__)

PAUSE_SECONDS = 5
MAX_TRIES = 10

class Servers:
    """Constellation of servers as defined in the instance map."""

    def __init__(self, instance_map):
        self.instance_map = instance_map
        self.servers = self._build_server_set(instance_map)
        self._cursor = 0

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
        self.pidfile = PIDFile(self.cfg['pgdata'])
        self.process = psutil.Process(self.pidfile.pid) if self.pidfile.pid else None

    @property
    def running(self):
        if self.process and psutil.pid_exists(self.process.pid):
            return True
        else:
            return False

    def start(self):
        """Start an instance."""
        if self.running:
            log.info('%s is already running' % self.name)

        else:
            os_args = [
                os.path.join(self.cfg['pgbinaries'], 'bin', 'pg_ctl'),
                'start',
            ]
            server_options = {
                'pgdata': self.cfg['pgdata'],
                'log': self.cfg['log'],
            }
            for arg, val in server_options.items():
                os_args.append('--%s=%s' % (arg, val))

            log.info('starting %s' % self.name)
            log.debug('args are: %s' % str(os_args))
            self.process = psutil.Popen(os_args)

            if not self.running:
                log.error('server %s did not start' % self.name)

        return self.running

    def stop(self):
        """Stop an instance."""
        if self.running:
            cnt = 0
            identifier = '%s (%d)' % (self.name, self.process.pid)
            while cnt < MAX_TRIES and self.running:
                msg = '%s not stopped yet, retrying' if cnt else 'stopping %s'
                log.info(msg % identifier)
                self.process.terminate()
                time.sleep(PAUSE_SECONDS)
                cnt += 1

            if self.running:
                err = 'server %s did not stop' % identifier
                log.error(err)
                raise errors.ServerStopError(err)
            else:
                log.info('%s has stopped' % identifier)
                self.process = None

        else:
            log.info('%s is already stopped' % self.name)

    def status(self):
        """Get status for an instance."""
        if self.running:
            print('%s (%d) is running with %d child processes' % (
                    self.name,
                    self.process.pid,
                    len(self.process.children())))
        else:
            print('%s is not running' % self.name)

    def restart(self):
        """Restart an instance."""
        log.info('restarting %s' % self.name)
        self.stop()
        self.start()


class PIDFile:
    """Abstraction around and utilities for PID files."""

    def __init__(self, pgdata_dir):
        self.path = os.path.join(pgdata_dir, 'postmaster.pid')

    @property
    def basename(self):
        return os.path.basename(self.path)

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
                return int(f.read())
        except IOError:
            raise
