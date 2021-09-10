#!/usr/bin/env python3

import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 7):
    sys.exit('Sorry, Python >=3.7 is required for DSRP.')

with open('requirements.txt') as f:
    reqs = []
    for line in f:
        line = line.strip()
        reqs.append(line.split('==')[0])


if __name__ == '__main__':
    setup(
        name='DSRP',
        version='1.0',
        description='Unified platform for dialogue research.',
        author='yen-nan ho',
        author_email='aaron1aaron2@gmail.com',
        python_requires='>=3.7',
        install_requires=reqs,
        include_package_data=True,
        package_data={'': ['*.txt', '*.md', '*.opt']},
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Topic :: Scientific/Engineering :: Artificial Intelligence :: Traffic",
            "Natural Language :: English",
        ],
    )