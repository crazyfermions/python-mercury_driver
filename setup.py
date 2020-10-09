# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# Authors
# Florian Forster <florian.forster@rwth-aachen.de>
# Sam Schott <ss2151@cam.ac.uk>

setup(name='mercuryitc',
      version='0.2.5',
      description='Full Python driver for the Oxford Mercury iTC cryogenic environment controller.',
      author='Florian Forster, Sam Schott',
      maintainer='Florian Forster',
      maintainer_email='florian.forster@rwth-aachen.de',
      url='https://github.com/crazyfermions/python-mercury_driver',
      licence='MIT',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      packages=find_packages(),
      install_requires=[
          'PyVISA',
          'pyvisa-py',
      ],
      zip_safe=False,
      )
