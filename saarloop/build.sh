#!/usr/bin/env bash

set -eux

SERVICENAME=$(cat servicename)
export SERVICENAME

# Build the service - the "service" directory will later be used to install.
# Can be empty if you build everything on the vulnbox. 
# You can remove files here that should never lie on the box.

apt-get install -y cmake libjsoncpp-dev libsndfile1-dev

# Examples:

# Build engine binary and delete its source
pushd service/engine && find . -not -name 'CMakeLists.txt' -not -name 'main.cpp' -delete && cmake . && make && find . -not -name 'CMakeLists.txt' -not -name 'saarloop_engine' -delete && popd
# Clean up django installation
pushd service && find . -type f -path '*/__pycache__/*' -delete && find . -type f  -not -name '__init__.py' -path '*/migrations/*' -delete && find . -not -type d -not -path './app/*' -not -path './data/samples/*' -not -path './data/synths/*' -not -path './engine/*' -not -path './saarloop/*' -not -path './static/*' -not -path './templates/*' -not -name 'manage.py' -not -name 'requirements.txt' -delete && find . -empty -not -name '__init__.py' -delete && popd
# Configure Django
# Disable debug mode
sed -i 's/DEBUG = True/DEBUG = False/' service/saarloop/settings.py
