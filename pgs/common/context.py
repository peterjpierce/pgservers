from argparse import ArgumentParser
import logging
import logging.config
from os.path import join

from etc import config, log
from pgs.common import errors, readers, util

DEFAULT_DESCRIPTION = 'Tools to manage PostgreSQL servers'


class ArgsWrapper():
    """Wraps argparse with common options, plus per-tool customizations."""

    def __init__(self, arg_definitions=[]):
        self.arg_definitions = arg_definitions

        try:
            description = arg_definitions['description']
        except KeyError:
            description = DEFAULT_DESCRIPTION

        self.parser = ArgumentParser(description=description)
        self._build()

    def parse(self):
        """Parse the command line and return results."""
        args = self.parser.parse_args()
        console_level = 'DEBUG' if args.verbose else 'ERROR' if args.quiet else 'INFO'
        return args, console_level

    def _build(self):
        """Initialize with common arguments."""
        def add(*args, **kwargs):
            self.parser.add_argument(*args, **kwargs)

        add('-v', '--verbose', action='store_true', help='show debug logging on console')
        add('-q', '--quiet', action='store_true', help='suppress non-error logging on console')

        if 'custom_args' in self.arg_definitions:
            for instrux in self.arg_definitions['custom_args']:
                add(*instrux['args'], **instrux['kwargs'])


def setup(toolname):
    """Learn and return context."""
    args_parser = ArgsWrapper(readers.load_arguments(toolname))
    args, console_logging_level = args_parser.parse()

    # optional per-app config
    try:
        app_config = readers.read_yaml(join(config.DIRS['config'], '%s.yml' % toolname))
    except errors.InputFileError:
        app_config = {}

    for k, v in app_config.items():
        setattr(config, k, v)

    # instance map
    instance_map = readers.read_yaml(join(config.DIRS['config'], 'instances.yml'))
    for inst_num, cfg in instance_map.items():
        # normalize keys to be strings
        if not isinstance(inst_num, str):
            instance_map[str(inst_num)] = cfg
            del instance_map[inst_num]

    # logging
    logfile = join(config.DIRS['log'], '%s.log' % toolname)
    util.make_parent_dir(logfile)
    logging_config = log.logging_config(logfile, console_level=console_logging_level)
    logging.config.dictConfig(logging_config)

    return args, instance_map
