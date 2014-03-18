#from distutils.core import setup
from setuptools import setup

setup(
    name='mercuryitc',
    version='0.1.0',
    description='A python based driver to control the Oxford MercuryITC system',
    long_description=open('README.rst').read(),
    url='https://github.com/crazyfermions/python-mercury_driver',
    author='Florian Forster',
    author_email='f.forster@physik.uni-muenchen.de',
    license='LICENSE.txt',
    packages=['mercuryitc'],
    install_requires=[
        "pyserial >= 2.6",
    ],
)
