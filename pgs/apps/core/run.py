import logging
from os.path import basename, dirname

from pgs.common import context, pgservers

TOOLNAME = basename(dirname(__file__))


def run():

    args, instance_map = context.setup(TOOLNAME)
    log = logging.getLogger(__name__)

    log.debug('received task "%s" for instances %s' % (args.operation, args.instances))
    servers = pgservers.Servers(instance_map)
    instances = instance_map.keys() if 'all' in args.instances else set(args.instances)
    invalid_instances = [i for i in instances if i not in servers.instance_names]

    if invalid_instances:
        log.error('invalid instance(s): %s' % str(invalid_instances))

    elif args.operation == 'list':
        print('\n'.join(servers.instance_names))

    elif args.operation == 'status':
        if not instances:
            instances = instance_map.keys()

        for instance in sorted(instances):
            servers.get_instance(instance).status()

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
