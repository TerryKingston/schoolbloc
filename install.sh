#!/bin/bash

set -e

# verify run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

# get domain from command line args
DOMAIN=$1
if [ -z "$DOMAIN" ]; then
    echo "Usage: ./install.sh <domain> (do not add www!)"
    echo "  example: ./install.sh schoolbloc.com"
    exit 1
fi

# Install apt depedencies
apt-get update
apt-get install -y apg
apt-get install -y nginx
apt-get install -y nodejs
apt-get install -y npm
apt-get install -y git
apt-get install -y git-core
apt-get install -y make
apt-get install -y ruby-dev
apt-get install -y ruby1.9.1
apt-get install -y build-essential
apt-get install -y libpq-dev
apt-get install -y libsqlite3-dev
apt-get install -y python3 python3-pip
apt-get install -y uwsgi
apt-get install -y uwsgi-plugin-python3
apt-get install -y uwsgi-plugin-python
ln -sf /usr/bin/nodejs /usr/bin/node

# Install system wide python packages
pip3 install virtualenv

# Setup directories where code will go
mkdir -p /var/www

# Clone code, move it into correct location
cd /root/
git clone -b production https://github.com/TerryKingston/schoolbloc.git
cp -r /root/schoolbloc/project_implementation/angular_app /var/www/httpdocs
cp -r /root/schoolbloc/project_implementation/flask_app /var/www/flask_app

# Setup angular app
npm install -g bower
npm install -g grunt-cli
cd /var/www/httpdocs
npm install
bower install --allow-root
gem install --no-rdoc --no-ri compass
cd /var/www/httpdocs/app
ln -sf ../bower_components/ .
ln -sf ../node_modules/ .

# Setup flask app
cd /var/www/flask_app
virtualenv venv
source /var/www/flask_app/venv/bin/activate
pip install -r /var/www/flask_app/requirements.txt
sed -ie "s/^SECRET_KEY\s*=.*$/SECRET_KEY = '$(apg -m 30 -x 35 -M NCL -a 1 -n 1)'/" config.py

# Install some demo data you can play around with
cp /root/schoolbloc/project_implementation/flask_app/schoolbloc/testing/sample_schedule_75_students.db schoolbloc.db

# Install z3
cd /root/
git clone https://github.com/Z3Prover/z3.git
cd /root/z3
python scripts/mk_make.py --python
cd /root/z3/build
make
make install

# Setup uwsgi runner
echo """[uwsgi]
socket = /tmp/flask.sock
virtualenv = /var/www/flask_app/venv
chdir = /var/www/flask_app
plugin = python3
module = run:app
processes = 4
threads = 2
stats = 127.0.0.1:9191
uid = www-data
gid = www-data
logto = /tmp/flask-uwsgi.log""" > /var/www/flask_app/uwsgi.ini

# Setup flask init script (using upstart)
echo """description \"Flask application driving schoolbloc\"

start on runlevel [2345]
stop on runlevel [!2345]
exec /usr/bin/uwsgi -c /var/www/flask_app/uwsgi.ini""" > /etc/init/flask.conf

# Disable any currently running nginx vhosts
rm /etc/nginx/sites-enabled/*

# Create the new nginx vhost
echo """server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    server_name www.$DOMAIN;

    root /var/www/httpdocs/app;
    index index.html index.htm;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location /auth {
        include uwsgi_params;
        uwsgi_param SCRIPT_NAME /;
        uwsgi_modifier1 30;
        uwsgi_pass unix:/tmp/flask.sock;
    }
    location /api/ {
        include uwsgi_params;
        uwsgi_param SCRIPT_NAME /;
        uwsgi_modifier1 30;
        uwsgi_pass unix:/tmp/flask.sock;
    }
}""" > /etc/nginx/sites-available/$DOMAIN.com.conf
cd /etc/nginx/sites-enabled
ln -sf ../sites-available/$DOMAIN.com.conf .

# Fix permissions
chown -R www-data:root /var/www/

# Start up uwsgi and nginx
start flask
service nginx restart

# Pretty finish message
echo "\n\n\n\nCongratulations! School block is now installed"
echo "The default username/password is 'admin' and 'admin'"
