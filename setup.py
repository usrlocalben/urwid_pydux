from os.path import abspath, dirname, join
from setuptools import setup, find_packages

INIT_FILE = join(dirname(abspath(__file__)), 'urwid_pydux', '__init__.py')

def get_version():
    with open(INIT_FILE) as fd:
        for line in fd:
            if line.startswith('__version__'):
                version = line.split()[-1].strip('\'')
                return version
        raise AttributeError('Package does not have a __version__')

setup(
    name='urwid_pydux',
    description='Urwid Components using the Pydux state container',
    long_description=open('README.rst').read(),
    url="http://github.com/benjamin9999/urwid_pydux/",
    version=get_version(),
    author='Benjamin Yates',
    author_email='benjamin@rqdq.com',
    packages=['urwid_pydux'],
    install_requires=['urwid>=1.3.0', 'pydux>=0.1.0'],
    license='MIT',
)
