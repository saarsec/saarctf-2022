#!/bin/sh

set -e

rm -rf v8_bundle v8_bundle.tar.xz
mkdir -p v8_bundle
cp -r v8/include v8_bundle/
cp v8/out.gn/x64.release.sample/obj/libv8_monolith.a v8_bundle
cp v8/out.gn/x64.release.sample/icudtl.dat v8_bundle

tar -c v8_bundle | xz -T0 > v8_bundle.tar.xz
ls -lh v8_bundle.tar.xz
