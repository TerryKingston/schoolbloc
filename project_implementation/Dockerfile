# Set the base image to Ubuntu
FROM buildpack-deps:jessie

# Update the repository
RUN apt-get update

# Install Nginx
# Add application repository URL to the default sources
RUN echo "deb http://archive.ubuntu.com/ubuntu/ raring main universe" >> /etc/apt/sources.list



# Install necessary tools
RUN apt-get install -y nano wget dialog net-tools

# Download and Install Nginx
RUN apt-get install -y nginx  

# Define working directory.
WORKDIR /etc/nginx

RUN mkdir /var/www/flask_app
ADD uwsgi.ini /var/www/flask_app
ADD flask.conf /etc/init
ADD school.conf /etc/nginx/sites-available/

# Install Python, flask and all our project requirements
# remove several traces of debian python
RUN apt-get purge -y python.*

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# gpg: key F73C700D: public key "Larry Hastings <larry@hastings.org>" imported
ENV GPG_KEY 97FC712E4C024BBEA48A61ED3A5CA953F73C700D

ENV PYTHON_VERSION 3.5.1

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 8.1.1

RUN set -ex \
	&& curl -fSL "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz \
	&& curl -fSL "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" -o python.tar.xz.asc \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" \
	&& gpg --batch --verify python.tar.xz.asc python.tar.xz \
	&& rm -r "$GNUPGHOME" python.tar.xz.asc \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	\
	&& cd /usr/src/python \
	&& ./configure --enable-shared --enable-unicode=ucs4 \
	&& make -j$(nproc) \
	&& make install \
	&& ldconfig \
	&& pip3 install --no-cache-dir --upgrade --ignore-installed pip==$PYTHON_PIP_VERSION \
	&& find /usr/local \
		\( -type d -a -name test -o -name tests \) \
		-o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		-exec rm -rf '{}' + \
	&& rm -rf /usr/src/python

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s easy_install-3.5 easy_install \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python-config3 python-config

# Install uwsgi dependencies
RUN pip install uwsgi

# Set the application directory
WORKDIR /var/www/flask_app

# Install our requirements.txt
ADD /flask_app/requirements.txt /var/www/flask_app/requirements.txt
RUN pip install -r requirements.txt

# Copy our code from the current folder to /app inside the container
ADD /flask_app/ . /var/www/flask_app/

# Installing angular_app dependencies
RUN     apt-get install -y nodejs npm git git-core
RUN     ln -s /usr/bin/nodejs /usr/bin/node

WORKDIR /var/www/httpdocs
ADD /angular_app/ . /var/www/httpdocs/

RUN     npm install -g bower 
RUN     npm install -g grunt-cli
RUN     npm install 
RUN     bower install --allow-root

# install ruby
RUN 	apt-get install -y -qq ruby-dev
RUN 	apt-get install make
RUN 	apt-get -qy install ruby1.9.1 build-essential libpq-dev libv8-dev libsqlite3-dev

#install compass
RUN 	gem install --no-rdoc --no-ri compass



