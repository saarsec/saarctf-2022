#!/usr/bin/env bash

set -eux

# Install the service on a fresh vulnbox. Target should be /home/<servicename>
# You get:
# - $SERVICENAME
# - $INSTALL_DIR
# - An user account with your name ($SERVICENAME)

# 1. Install dependencies
apt-get update
apt-get install -y cmake build-essential gcc g++ git \
  libjsoncpp-dev uuid-dev libssl-dev zlib1g-dev libsqlite3-dev libc-ares-dev libbrotli-dev \
  python3-minimal python3-requests python3-brotli sqlite3

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
mkdir "$INSTALL_DIR/build"
pushd .
cd "$INSTALL_DIR/build"
cmake ..
make -j8 SaarCloud
popd
# create data directory
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/static"
mkdir -p "$INSTALL_DIR/databases"
mkdir -p "$INSTALL_DIR/build/uploads"
touch "$INSTALL_DIR/application_secret"
cp "$INSTALL_DIR/default.js" "$INSTALL_DIR/default_bcp.js"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR/scripts" "$INSTALL_DIR/static" "$INSTALL_DIR/databases" "$INSTALL_DIR/build/uploads" "$INSTALL_DIR/application_secret"
rm -rf "$INSTALL_DIR/scripts/default.js" "$INSTALL_DIR/static/default"
pushd .
cd "$INSTALL_DIR/scripts"
ln -s ../default.js ./
cd ../static
ln -s ../default-frontend ./default
popd
chown -h root:root "$INSTALL_DIR/scripts/default.js" "$INSTALL_DIR/static/default"



# 3. Configure startup for your service
# Typically use systemd for that:
# Install backend as systemd service
# Hint: you can use "service-add-simple '<command>' '<working directory>' '<description>'"
# service-add-simple "$INSTALL_DIR/TODO-your-script-that-should-be-started.sh" "$INSTALL_DIR/" "<TODO>"
service-add-simple "$INSTALL_DIR/run.sh" "$INSTALL_DIR/build" "SaarCloud service"

# Example: Cronjob that removes stored files after a while
# cronjob-add "*/6 * * * * find $INSTALL_DIR/data -mmin +45 -type f -delete"


# 4. Add some demo sites so that players see where the flags will be
pushd .
cd "$INSTALL_DIR/build"
sudo -Hu $SERVICENAME timeout 20 ./SaarCloud &
PID=$!
popd

cd checkers
# use 127.1.0.1 instead of 127.0.0.1 to circumvent some router-based DNS-Rebinding protections
python3 -u demo_website_generator.py 127.1.0.1
cd ..

echo "Terminating ..."
kill -s TERM $PID
wait $PID || true

# Wipe credentials again
truncate -s 0 "$INSTALL_DIR/application_secret"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR/application_secret"
