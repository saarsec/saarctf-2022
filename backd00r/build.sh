#!/usr/bin/env bash

set -eux

apt-get update
apt-get install -y build-essential make cmake \
  libnl-3-dev libnl-genl-3-dev libnl-route-3-dev libgcrypt-dev \
  linux-headers-amd64

# 1. build kernel module
cd service/r00t-kernel
make containerbuild
cp r00t.ko ../
cd ../..

# 2. build client
mkdir service/build-client service/build-patchelf
cd service/build-patchelf
cmake ../elfpatch
make
cd ../../service/build-client
cmake ../r00t-client -DCMAKE_MODULE_PATH=../cmake
make -j "$(nproc)" r00t-raw-client r00t-raw-client-docker
../build-patchelf/patchelf r00t-raw-client
../build-patchelf/patchelf r00t-raw-client-docker
#strip r00t-raw-client
#strip r00t-raw-client-docker
cp r00t-raw-client ../backd00r
cp r00t-raw-client-docker ../backd00r-docker
cd ../..

# 3. remove source
rm -rf service/cmake service/r00t-client service/r00t-kernel* service/CMakeLists.txt service/build-client service/cmake-build-*

# Examples:
# cd service && make -j4  # build C binary
# cd service && npm install && npm run build  # use npm to build a frontend
# rm -rf service/.idea  # remove files that should not be on vulnbox
