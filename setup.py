#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from dojo import Dojo

def find_data_files(directory):
    return [(path, [path+os.sep+f for f in files])
            for path, _, files in os.walk(directory)]

print Dojo.resource_dir
setup(name = 'pyweek-dojo',
      version = Dojo.version,
      description = Dojo.__doc__,
      packages = find_packages(),
      data_files=find_data_files("resource"),
      entry_points = {'gui_scripts': ['Dojo = dojo:main']},
     )

