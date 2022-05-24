#!/usr/bin/env bash

set -eux

export PORT=1984

# Install the service on a fresh vulnbox. Target should be /home/<servicename>
# You get:
# - $SERVICENAME
# - $INSTALL_DIR
# - An user account with your name ($SERVICENAME)

# 1. Install dependencies
apt-get update
apt-get install -y python3 nginx python3-wheel python3-pip
pip3 install uwsgi
chmod +x /usr/local/bin/uwsgi  # Bugfix (?)
pip3 install -r service/$SERVICENAME/requirements.txt

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR"
sudo -u "$SERVICENAME" python3 "$INSTALL_DIR/$SERVICENAME/manage.py" collectstatic --no-input


# 3.init database:
sudo -u "$SERVICENAME" python3 "$INSTALL_DIR/$SERVICENAME/manage.py" makemigrations
sudo -u "$SERVICENAME" python3 "$INSTALL_DIR/$SERVICENAME/manage.py" migrate
# regenerate secret key
rm -rf "$INSTALL_DIR/bytewarden/.secret.key"

# 4. Configure the server
# Copied from saarloop (@jkrupp)
cat - > /etc/nginx/sites-available/$SERVICENAME <<EOF
server {
    listen $PORT;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/$SERVICENAME.sock;
    }
}
EOF
ln -s /etc/nginx/sites-available/$SERVICENAME /etc/nginx/sites-enabled/$SERVICENAME

cat - > $INSTALL_DIR/uwsgi.ini <<EOF
[uwsgi]
chdir=$INSTALL_DIR/$SERVICENAME
wsgi-file=$INSTALL_DIR/$SERVICENAME/$SERVICENAME/wsgi.py
master=true
processes=4
#harakiri=20
max-requests=5000
vacuum=true
static-map=/static=$INSTALL_DIR/$SERVICENAME/$SERVICENAME/static
daemonize=/$INSTALL_DIR//%n.log
socket=/tmp/$SERVICENAME.sock
chmod-socket=777
EOF


# 5. Configure startup for your service
# Debug with default Django runserver
# service-add-simple "python3 $INSTALL_DIR/$SERVICENAME/manage.py runserver 0.0.0.0:$PORT --insecure" "$INSTALL_DIR/" "Bytewarden service"

# Copied from saarloop (@jkrupp)
service-add-advanced "/usr/local/bin/uwsgi $INSTALL_DIR/uwsgi.ini" "$INSTALL_DIR/" "$SERVICENAME service" <<'EOF'
KillSignal=SIGQUIT
NotifyAccess=all
Restart=always
RestartSec=5
EOF
sed -i 's/Type=simple/Type=forking/' "/etc/systemd/system/$SERVICENAME.service"


# Example: Cronjob that removes stored files after a while
# cronjob-add "*/6 * * * * find $INSTALL_DIR/data -mmin +45 -type f -delete"

# Flush db every 30 minutes
# cronjob-add "*/30 * * * * python3 '$INSTALL_DIR/$SERVICENAME/manage.py' flush --no-input"



