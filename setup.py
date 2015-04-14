# -*- coding: utf-8 -*-
import re
import sys
import subprocess

import pip
from setuptools import setup, find_packages


def parse_requirements(requirements):
    with open(requirements) as f:
        return [
            l.strip('\n') for l
            in f if l.strip('\n') and not l.startswith('#')
        ]


def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version("modularodm/__init__.py")

PUBLISH_CMD = "python setup.py register sdist bdist_wheel upload"
TEST_PUBLISH_CMD = 'python setup.py register -r test sdist bdist_wheel upload -r test'
TEST_CMD = 'nosetests'

if 'publish' in sys.argv:
    try:
        __import__('wheel')
    except ImportError:
        print("wheel required. Run `pip install wheel`.")
        sys.exit(1)
    status = subprocess.call(PUBLISH_CMD, shell=True)
    sys.exit(status)

if 'publish_test' in sys.argv:
    try:
        __import__('wheel')
    except ImportError:
        print("wheel required. Run `pip install wheel`.")
        sys.exit(1)
    status = subprocess.call(TEST_PUBLISH_CMD, shell=True)
    sys.exit()

if 'run_tests' in sys.argv:
    try:
        __import__('nose')
    except ImportError:
        print('nose required. Run `pip install nose`.')
        sys.exit(1)

    status = subprocess.call(TEST_CMD, shell=True)
    sys.exit(status)


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='modular-odm',
    version=__version__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    url="https://github.com/CenterForOpenScience/modular-odm",
    author='Center for Open Science',
    author_email='contact@centerforopenscience.org',
    zip_safe=False,
    description='A Pythonic Object Data Manager',
    long_description=read("README.rst"),
    packages=find_packages(exclude=("test*",)),
    install_requires=parse_requirements('requirements.txt'),
    tests_require=["nose"],
    keywords=["odm", "nosql", "mongo", "mongodb"],
)
