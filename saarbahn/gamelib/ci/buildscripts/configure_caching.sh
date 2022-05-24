#!/usr/bin/env bash
set -euxo pipefail

# Ensure cache directories exist
mkdir -p \
  "$CI_PROJECT_DIR"/.cache/apt/lists/partial \
  "$CI_PROJECT_DIR"/.cache/apt/archives/partial \
  "$CI_PROJECT_DIR"/.cache/pip \
  "$CI_PROJECT_DIR"/.cache/npm

# Configure APT for caching
if [ -d "/etc/apt" ]; then
  if ! timeout 3 "$CI_PROJECT_DIR/gamelib/ci/buildscripts/test-and-configure-aptcache.sh"; then
    echo "dir::state::lists    $CI_PROJECT_DIR/.cache/apt/lists;" >> /etc/apt/apt.conf
    echo "dir::cache::archives    $CI_PROJECT_DIR/.cache/apt/archives;" >> /etc/apt/apt.conf
  fi

  if ! wget > /dev/null 2>&1 ; then
    apt-get update
    apt-get install -y --no-install-recommends wget ca-certificates
  fi
fi
