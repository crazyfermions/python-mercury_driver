from setuptools import setup, find_packages

setup(name="mercuryitc",
      version="0.1.1",
      description="Full Python driver for the Oxford Mercury iTC cryogenic environment controller.",
      author="Sam Schott",
      author_email="ss2151@cam.ac.uk",
      author='Florian Forster, Sam Schott',
      author_email='f.forster@physik.uni-muenchen.de',
      url='https://github.com/crazyfermions/python-mercury_driver',
      licence='MIT',
      long_description=open('README.md').read(),
      packages=find_packages(),
      install_requires=[
          'PyVISA',
          'pyvisa-py',
      ],
      zip_safe=False,
      )
