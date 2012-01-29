#!/bin/sh

# This script creates the source and Mac application bundles

# Delete folders from earlier builds
rm -R build

# Create the application using py2app
python setup.py py2app

# Create the source distribution
python setup.py source

# Finally delete temporary directories created during the build process
rm -R build

