#!/usr/bin/env bash

set -eu

echo 'Container start at' "$(date)"
echo 'Bound IP addresses:' > /machine-infos.txt
ip addr | egrep -o 'inet [0-9]+\.[0-9]+\.[0-9]+\.[0-9]' >> /machine-infos.txt
cat /machine-infos.txt
