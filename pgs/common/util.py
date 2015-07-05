import errno
import os


def make_dir(dirpath):
    """Make directories for a given path, raising OSError if trouble."""
    try:
        os.makedirs(dirpath)
    except OSError as err:
        if err.errno == errno.EEXIST:
            pass
        else:
            raise


def make_parent_dir(filepath):
    """Make and return the path for the directory enclosing filepath."""
    parent_dir = os.path.dirname(filepath)
    make_dir(parent_dir)
    return parent_dir
