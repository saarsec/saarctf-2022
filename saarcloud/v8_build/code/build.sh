#!/bin/sh

set -e

# Install depot_tools
cd /tools
if [ ! -d depot_tools ]; then
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
fi
export PATH=/tools/depot_tools:$PATH
echo $PATH

# try to build v8
cd /v8

# TODO
#exec sleep infinity
#rm -rf out.gn/x64.release.sample

if [ ! -d out.gn/x64.release.sample ]; then
  tools/dev/v8gen.py gen x64.release.sample
fi

#ls -la out.gn
ninja -C out.gn/x64.release.sample v8_monolith

# /usr/bin/python -u tools/mb/mb.py gen -f infra/mb/mb_config.pyl -m developer_default -b x64.release.sample out.gn/x64.release.sample
