#!/usr/bin/env bash
set -euxo pipefail

SCRIPTPATH="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
source "${SCRIPTPATH}/../include/detect-docker"

# Docker only - install systemd handler, remove the rest
if detect-docker; then
  cp /opt/gamelib/ci/docker-systemd/* /opt/
  rm -rf /opt/gamelib /opt/service
  rm -rf /tmp/*
fi
