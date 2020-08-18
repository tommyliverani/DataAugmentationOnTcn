# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='examon-client',
      version='0.3.1',
      description='Examon client',
      url='http://github.com/fbeneventi/examon_client',
      author='Francesco Beneventi',
      author_email='francesco.beneventi@unibo.it',
      license='MIT',
      packages=['examon'],      
      install_requires=[
          'pytz',
          'cachetools',
          'pandas >= 0.20.0'
      ],
      zip_safe=False)