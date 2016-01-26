# Flask.py Implementation

## Installation

### Mac OSX

*assuming [Homebrew](http://brew.sh/) is installed*

```bash
brew install python3
```

install virtual env

```bash
pip3 install virtualenv
```

setup virtualenv (do this in the project root folder!)
```bash
virtualenv venv
```

activate virtualenv
```bash
source venv/bin/activate
```

install the project dependencies
```bash
pip3 install -r project_implementation/flask_app/requirements.txt
```

run the flask app
```bash
python run.py
```

the flask app should now be running at http://0.0.0.0:5000/