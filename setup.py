#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='ret1',
    version='0.1',
    author='Chris Turner',
    author_email='cat@199tech.net',
    description='datajoint ret1 demo',
    license='proprietary',
    keywords='datajoint demo',
    url='http://fixme.io',
    packages=find_packages(include=['ret1']),
    scripts=['ret1/bin/test.py']
)
