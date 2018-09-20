from setuptools import setup, find_packages

setup(name="MercuryiTC",
      version="0.1.0",
      description="Full Python driver for the Oxford Mercury iTC cryogenic environment controller.",
      url="https://github.com/OE-FET/MercuryiTC.git",
      author="Sam Schott",
      author_email="ss2151@cam.ac.uk",
      licence='MIT',
      long_description=open('README.md').read(),
      packages=find_packages(),
      install_requires=[
          'PyVISA',
          'pyvisa-py',
          'threading',
          'setuptools',
      ],
      zip_safe=False,
)
