import logging
from os.path import basename, dirname

from pgs.common import context, pgservers

TOOLNAME = basename(dirname(__file__))


def print_status_table(server_list):
    """Output a formatted status table."""
    fmt = '%-10s  %4s  %-5s  %5s  %7s  %s'
    headings = ('instance', 'port', 'state', 'PID', 'threads', 'databases')
    print('%s\n%s' % (fmt % headings, '-' * 60))

    for server in server_list:

        if server.running:
            state, pid, thread_count = 'up', server.pidfile.pid, 1 + len(server.process.children())
        else:
            state, pid, thread_count = 'down', '', ''

        print(fmt % (
            server.name,
            str(server.cfg['pgport']),
            state,
            str(pid),
            str(thread_count),
            ', '.join(server.database_names)
        ))


def run():

    args, instance_map = context.setup(TOOLNAME)
    log = logging.getLogger(__name__)

    log.debug('received task "%s" for instances %s' % (args.operation, args.instances))
    servers = pgservers.Servers(instance_map)
    instances = instance_map.keys() if 'all' in args.instances else set(args.instances)
    invalid_instances = [i for i in instances if i not in servers.instance_names]

    if invalid_instances:
        log.error('invalid instance(s): %s' % str(invalid_instances))

    elif args.operation == 'status':
        show = [s for s in servers if s.name in instances] if instances else servers
        print_status_table(show)

    else:
        if not instances:
            print('provide instance(s)')

        for instance in sorted(instances):
            server = servers.get_instance(instance)
            log.info('performing %s for %s' % (args.operation, server.name))
            method = getattr(server, args.operation)
            method()


if __name__ == '__main__':
    run()
