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
apt-get install -y python3 nginx python3-wheel python3-pip python3-setuptools libjsoncpp24 libsndfile1 # systemd
pip3 install uwsgi
chmod +x /usr/local/bin/uwsgi  # Bugfix (?)
pip3 install -r service/requirements.txt

# 2. TODO Copy/move files
mv service/* "$INSTALL_DIR/"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR"

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
cat - > /etc/nginx/sites-available/$SERVICENAME <<EOF
server {
    listen 11025;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/saarloop.sock;
    }
}
EOF
ln -s /etc/nginx/sites-available/$SERVICENAME /etc/nginx/sites-enabled/$SERVICENAME


cat - > $INSTALL_DIR/uwsgi.ini <<EOF
[uwsgi]
chdir=$INSTALL_DIR
wsgi-file=$INSTALL_DIR/saarloop/wsgi.py
master=true
processes=4
#harakiri=20
max-requests=5000
vacuum=true
static-map=/static=$INSTALL_DIR/static
daemonize=/$INSTALL_DIR//%n.log
socket=/tmp/saarloop.sock
chmod-socket=777
EOF


# 4. TODO Configure startup for your service
# Typically use systemd for that:
# Install backend as systemd service
# Hint: you can use "service-add-simple '<command>' '<working directory>' '<description>'"
# service-add-simple "$INSTALL_DIR/TODO-your-script-that-should-be-started.sh" "$INSTALL_DIR/" "<TODO>"
service-add-advanced "/usr/local/bin/uwsgi $INSTALL_DIR/uwsgi.ini" "$INSTALL_DIR/" "$SERVICENAME service" <<'EOF'
KillSignal=SIGQUIT
NotifyAccess=all
Restart=always
RestartSec=5
EOF
sed -i 's/Type=simple/Type=forking/' "/etc/systemd/system/$SERVICENAME.service"

# Example: Cronjob that removes stored files after a while
# cronjob-add "*/6 * * * * find $INSTALL_DIR/data -mmin +45 -type f -delete"



# Example: Initialize Databases (PostgreSQL example)

# Example: 5. Startup database (CI DOCKER ONLY, not on vulnbox)
# if detect-docker; then
#     EXAMPLE for PostgreSQL: pg_ctlcluster 11 main start
# fi

# Example: 6. Configure PostgreSQL
# cp $INSTALL_DIR/*.sql /tmp/
# sudo -u postgres psql -v ON_ERROR_STOP=1 -f "/tmp/init.sql"
sudo -u "$SERVICENAME" python3 "$INSTALL_DIR/manage.py" makemigrations && python3 "$INSTALL_DIR/manage.py" migrate
rm -rf "$INSTALL_DIR/.secret.key"

# Example: 7 Stop services (CI DOCKER ONLY)
# if detect-docker; then
#     pg_ctlcluster 11 main stop
# fi
