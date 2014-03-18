#from distutils.core import setup
from setuptools import setup

setup(
    name='mercuryitc',
    version='0.1.0',
    description='A python based driver to control the Oxford MercuryITC system',
    long_description=open('README.rst').read(),
    author='Florian Forster',
    author_email='f.forster@physik.uni-muenchen.de',
    license='MIT',
    packages=['mercuryitc'],
    install_requires=[
        "pyserial >= 2.6",
    ],
)
