#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='glacier-tests',
    version='0.0.1',
    packages=find_packages(),

    author='Timur Alperovich',
    author_email='timur.alperovich@gmail.com',
    description='Unofficial Amazon Glacier tests',
    license='MIT',
    keywords='glacier tests',

    install_requires=[
        'boto >=2.38',
        ],
    )
