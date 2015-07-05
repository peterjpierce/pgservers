from os.path import abspath, dirname, join

base_dir = abspath(join(dirname(__file__), '..'))
DIRS = {
    'app': base_dir,
    'config': abspath(dirname(__file__)),
    'log': join(base_dir, 'var', 'log')
}
