from os.path import abspath, dirname, join

import yaml

from pgs.common import errors

DEFAULT_DELIMITER = '\t'


def read_yaml(yaml_filepath):
    """Load contents of a YAML file."""
    try:
        with open(yaml_filepath, 'rb') as f:
            return yaml.load(f)
    except IOError as err:
        raise errors.InputFileError(err)


def load_arguments(toolname):
    """Load tool-specific arguments."""
    defs_file = abspath(join(dirname(__file__), '..', 'apps', toolname, 'args.yml'))
    try:
        arguments = read_yaml(defs_file)
    except IOError:
        arguments = {}
    return arguments
