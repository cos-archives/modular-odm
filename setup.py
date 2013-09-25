from setuptools import setup, find_packages
from pip.req import parse_requirements

setup(
    name='modular-odm',
    version='0.2',
    author='Center for Open Science',
    author_email='contact@centerforopenscience.org',
    description='A Pythonic Object Data Manager',
    packages=find_packages(),
    install_requires=[
        str(req.req) 
        for req in parse_requirements('requirements.txt')
    ],
)
