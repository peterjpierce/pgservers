import logging

from pgs.common import errors, context, servers


def run():

    args, instance_map = context.setup()
    log = logging.getLogger(__name__)

    log.debug('received task "%s" for instances %s' % (args.task, args.instances))
    instances = instance_map.keys() if 'all' in args.instances else set(args.instances)

    for instance in sorted(instances):

        try:
            server = servers.GunicornServer(instance, instance_map)
        except errors.InvalidServerError as err:
            log.warn('instance "%s" is not valid, skipping' % instance)
            continue

        log.info('performing %s for %s' % (args.task, server.name))
        meth = getattr(server, args.task)
        meth()


if __name__ == '__main__':
    run()
