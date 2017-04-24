#! python3.6
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    Licence = f.read()

setup(
    name='Bataille navale',
    version='1.3.0',
    description='Jeu de société PVP / PVE',
    long_description=readme,
    license="GPLv3",
    author="Nicolas Vincent"
    author_email='nicolas.vincent100@gmail.com',
    url='https://github.com/NicovincX2/Battleship',
    packages=find_packages(exclude=('tests', 'docs'))
    install_requires=['numpy','pandas']
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Board games",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: French",
        "Operating System :: OS Independent"
    ],
)
