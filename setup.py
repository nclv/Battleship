#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import io

import naval_battle

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    """Lit plusieurs fichiers et les assemble.
    """
    
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='Bataille navale',
    version=naval_battle.__version__,
    description='Jeu de société PVP / PVE',
    long_description=long_description,
    license="GPLv3",
    author="Nicolas Vincent",
    author_email='nicolas.vincent100@gmail.com',
    url='https://github.com/NicovincX2/Battleship',
    install_requires=['numpy','pandas'],
    packages=find_packages(exclude=['docs']),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Board games",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: French",
        "Operating System :: OS Independent"
    ],
)
