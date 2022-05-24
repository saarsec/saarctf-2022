#!/usr/bin/env bash
set -euxo pipefail

# Run after all other steps, create badges that are missing so far (because step has not been run)

function makebadge {
  wget "https://img.shields.io/badge/$1" -O "public/$2"
}

mkdir -p public
test -f public/ci-build.svg || makebadge build-skipped-inactive ci-build.svg
test -f public/ci-install.svg && makebadge install-ok-brightgreen ci-install.svg || true
test -f public/ci-install.fail && makebadge install-failed-red ci-install.svg && rm public/ci-install.fail || true
test -f public/ci-install.svg || makebadge install-skipped-inactive ci-install.svg
test -f public/ci-checkers.svg || makebadge checkers-skipped-inactive ci-checkers.svg
test -f public/ci-exploits.svg || makebadge exploits-skipped-inactive ci-exploits.svg

export TZ=Europe/Berlin
makebadge "updated-`date '+%d.%m.%Y'`-blue" ci-update.svg
makebadge "updated-`date '+%d.%m.%Y %H:%M'`-blue" ci-update2.svg
