# Angular.js Implementation

## Setup
Angular.js depends on npm.  To install npm, run:

	sudo apt-get update
	sudo apt-get install npm
	npm install --global npm@latest

To get grunt to work, run:

	npm install --global yo bower grunt-cli

Check all was installed correctly:

	yo --version && bower --version && grunt --version

For compass to work, you may have to install it as well

	sudo apt-get install ruby-compass
	sudo gem install compass

Lastly, if you are under an ubuntu firewall, make sure to allow for port 9000 and for live reload (35729):

	sudo ufw allow 9000/tcp
	sudo ufw allow 35729/tcp
	sudo shutdown -r now

## Compile
To compile, in the `angular_app` directory, run:

	npm install

## Run
Once compiled, run:

	grunt serve

to have grunt start listening for connections on port 9000. (Obviously, the port can be modified as need be)