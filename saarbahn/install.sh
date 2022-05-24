#!/usr/bin/env bash

set -eux

# Install the service on a fresh vulnbox. Target should be /home/<servicename>
# You get:
# - $SERVICENAME
# - $INSTALL_DIR
# - An user account with your name ($SERVICENAME)

# 1. TODO Install dependencies
# EXAMPLE: apt-get install -y nginx
apt-get update
apt-get install -y socat postgresql curl libpq-dev default-libmysqlclient-dev libsqlite3-dev sqlite3
# debug utilities
apt-get install -y procps file netcat vim

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > $HOME/tmp.sh
if mount | grep '/dev/shm' | grep -q 'noexec'; then
    mkdir -p /root/tmp
    export TMPDIR=/root/tmp 
else
    export TMPDIR=/dev/shm
fi
sh $HOME/tmp.sh -y
rm -f $HOME/tmp.sh
source $HOME/.cargo/env
echo '. $HOME/.cargo/env' >> /root/.bash_profile
cargo install diesel_cli

# 2. TODO Copy/move files
mv service/saarbahn "$INSTALL_DIR/"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR"
cd "$INSTALL_DIR/saarbahn"
cargo build # --release

# Cleanup
rm -rf /root/tmp
unset TMPDIR
rm -rf target/debug/deps target/debug/examples target/debug/incremental target/debug/build
rm -rf /root/.rustup/toolchains/*/share/doc/rust

#ln -s target/release/saarbahn /home/saarbahn/
# mv service/saarbahn "$INSTALL_DIR/"
# mv service/initDB.sql "$INSTALL_DIR/"
# mv run.sh "$INSTALL_DIR/"
# rm -rf service/
# rm -rf build.sh  dependencies.sh  install.sh
# ls
# chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR"
# cd /home/saarbahn
# 3. TODO Configure the server
# ...
# For example:
# - adjust configs of related services (nginx/databases/...)
# - Build your service if there's source code on the box
# - ...
#
# Useful commands:
# - nginx-location-add <<EOF
#   location {} # something you want to add to nginx default config (port 80)
#   EOF


#cronjob-add-root "*/5 * * * * sudo -u postgres psql -p 5434 -d vault -w -c \"delete from data where (now() - created_at)::time > '00:30:00'::time;\" "
#cronjob-add-root "*/5 * * * * sudo -u postgres psql -p 5434 -d vault -w -c \"delete from users where (now() - created_at)::time > '00:30:00'::time;\" "

# 4. TODO Configure startup for your service
# Typically use systemd for that:
# Install backend as systemd service
# Hint: you can use "service-add-simple '<command>' '<working directory>' '<description>'"
# service-add-simple "$INSTALL_DIR/TODO-your-script-that-should-be-started.sh" "$INSTALL_DIR/" "<TODO>"
# service-add-simple "socat -s -T10 TCP-LISTEN:31337,reuseaddr,fork EXEC:bash,pty,stderr,setsid,sigint,sane" "$INSTALL_DIR/" "<TODO>"
#service-add-simple "socat -s -T60 TCP-LISTEN:4711,fork,reuseaddr EXEC:\"./vault\",setsid" "$INSTALL_DIR/" "Vault"
# Example: Cronjob that removes stored files after a while
# cronjob-add "*/6 * * * * find $INSTALL_DIR/data -mmin +45 -type f -delete"
# service-add-simple "socat -s -T60 TCP-LISTEN:31337,fork,reuseaddr EXEC:\"/home/saarbahn/service/saarbahn/target/debug/saarbahn\",setsid" "$INSTALL_DIR/" "Saarbahn"
service-add-simple "$INSTALL_DIR/saarbahn/target/debug/saarbahn" "$INSTALL_DIR/saarbahn" "saarbahn"

# pg_createcluster -p 5434 -e UTF8 13 saarbahn

sed 's/local   all             all                                     peer/local   all             all                                     md5/g' /etc/postgresql/13/main/pg_hba.conf > tmp
mv tmp /etc/postgresql/13/main/pg_hba.conf
# systemctl enable postgresql@13-saarbahn
# Example: 5. Startup database (CI DOCKER ONLY, not on vulnbox)
if detect-docker; then
    pg_ctlcluster 13 main start
#else
#    systemctl start postgresql@13-saarbahn
fi

# Example: 6. Configure PostgreSQL
cd /tmp/
sudo -u postgres psql -p 5432 -v ON_ERROR_STOP=1 <<EOF
CREATE ROLE $SERVICENAME LOGIN VALID UNTIL 'infinity';
ALTER ROLE $SERVICENAME PASSWORD 'password';
CREATE DATABASE $SERVICENAME WITH ENCODING='UTF8' CONNECTION LIMIT=-1;
GRANT ALL PRIVILEGES ON DATABASE $SERVICENAME TO $SERVICENAME;
EOF
cd "$INSTALL_DIR/saarbahn"
diesel migration run
# Example: 7 Stop services (CI DOCKER ONLY)
if detect-docker; then
    pg_ctlcluster 13 main stop
fi
