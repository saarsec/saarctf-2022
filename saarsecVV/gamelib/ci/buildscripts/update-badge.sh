#!/usr/bin/env bash
set -euxo pipefail

# ARGUMENTS: <badge name> (as $CI_JOB_NAME)

if test -f ".nobadge"; then
  exit 0
elif test -f ".missing"; then
  BADGE="$CI_JOB_NAME-missing-yellow"
elif test -f ".success"; then
  BADGE="$CI_JOB_NAME-ok-brightgreen"
else
  BADGE="$CI_JOB_NAME-failed-red"
fi

mkdir -p public
BADGE_FILENAME="public/ci-$CI_JOB_NAME.svg"
wget "https://img.shields.io/badge/$BADGE" -O "$BADGE_FILENAME"
ls -la public
