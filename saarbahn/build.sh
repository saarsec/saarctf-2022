#!/usr/bin/env bash

set -eux

SERVICENAME="saarbahn"
export SERVICENAME
# cd service && cargo build --release
# Build the service - the "service" directory will later be used to install.
# Can be empty if you build everything on the vulnbox. 
# You can remove files here that should never lie on the box.

#sed -i '/^\s*\/\//d' service/saarbahn/src/comment.rs

# Examples:
# cd service && make -j4  # build C binary
# cd service && npm install && npm run build  # use npm to build a frontend
# rm -rf service/.gitignore service/*.iml service/.idea  # remove files that should not be on vulnbox
# rm -rf service/node_modules service/*.log service/data  # remove more things that might occur
