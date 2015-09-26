Quick Start
-----------
I have all of this code running on webserv.vimalloc.com:5000. Go to these
routes, and compare it to the code in app.py and the html in templates/ for
a quick example of working in flask

* http://webserv.vimalloc.com:5000/
* http://webserv.vimalloc.com:5000/test
* http://webserv.vimalloc.com:5000/redirect
* http://webserv.vimalloc.com:5000/template
* http://webserv.vimalloc.com:5000/data/put-anything-here
* http://webserv.vimalloc.com:5000/forms
* http://webserv.vimalloc.com:5000/exception


Local Setup
------------
Note: If anyone is looking for an IDE, pycharm is fantastic (and has a great vim
emulation mode if you like that), and we get a free subscription to it by being
students. Highly recommend it.

Ok, so this example has some dependencies, and the best way to not clutter up
your system is using a python virtual enviornmnet. The tool that can create
virtual enviornments for you is called virtualenv (it can be installed through
pip if it isn't otherwise availble on your system). If you have any trouble
installing pip or installing this let me know and I can help out.

To create a new virtual enviornment run:
```bash
cd /path/to/save/this/at
virtualenv venv
```

To activate the new virtual enviornment, run
```bash
source venv/bin/activate
```

and to deactive it, run
```bash
deactivate
```

To install all of the dependencies that this probject needs to run (while the
virtual enviornment is activated)
```bash
pip install -r skag-senior-project/technology_examples/flask/requirements.txt
```

And now you should be able to run the example (again with the venv activated) by running
```bash
python app.py
```

Flask
-----
This is only a small example of what flask can do, but should give a good idea
about the modular nature of working in the flask framework. Some additional
feature of flask we will likely take advantage of are:

* Proper restful api library
* Session management and user logins
* Offload long running tasks to a worker application (ie gearman/celery/etc)
* Modular design
* Different development and production enviornments
* ORM for database stuff
* Unit test
