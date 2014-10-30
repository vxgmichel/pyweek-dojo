#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def find_data_files(directory):
    return [(path, [path+os.sep+f for f in files])
            for path, _, files in os.walk(directory)]

setup(name = 'pyweek-dojo',
      version = '1.1.0',
      description = 'A minimalistic versus fighting game',
      packages = find_packages(),
      data_files=find_data_files("resource"),
      entry_points = {'gui_scripts': ['Dojo = dojo:main']},
     )

