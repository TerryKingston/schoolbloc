FROM    ubuntu:14.04

RUN     apt-get update
RUN     apt-get install -y nodejs npm git git-core
RUN     ln -s /usr/bin/nodejs /usr/bin/node
ADD . /app

WORKDIR /app

RUN     npm install -g bower 
RUN     npm install -g grunt-cli
RUN     npm install 
RUN     bower install --allow-root

# install ruby
RUN 	apt-get install -y -qq ruby-dev
RUN 	apt-get install make

#install compass
RUN 	gem install --no-rdoc --no-ri compass
EXPOSE 9000