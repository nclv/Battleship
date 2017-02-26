# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    Licence = f.read()

setup(
    name='Bataille navale',
    version='0.1.0',
    description='Jeu de société PVP / PVE',
    long_description=readme,
    author='Vincent Nicolas',
    author_email='nicolas.vincent100@gmail.com',
    url='https://github.com/NicovincX2',
    license=License,
    packages=find_packages(exclude=('tests', 'docs'))
)
