"""
This is an example views declaration file for a blueprint.

This is where we import any objects or data that we may need to interact with
and expose it to the world via http requests
"""
import logging
from flask import Blueprint, jsonify, render_template
from schoolbloc.blueprint.forms import ExampleForm
from schoolbloc.blueprint.models import ExampleUser

# Blueprint settings
mod = Blueprint('blueprint-name', __name__, template_folder='templates')

# Setup logger
log = logging.getLogger(__name__)


@mod.route('/blueprint/test1', methods=['GET'])
def test1():
    """ Just return a string to the caller """
    return 'hello world'


@mod.route('/blueprint/test2', methods=['GET'])
def test2():
    """ Just return a string to the caller """
    return render_template('example.html')


@mod.route('/blueprint/test3', methods=['GET'])
def test3():
    """ Converts python data structures to json and returns them to the caller """
    sample_data = {
        'hello': 'world',
        'foo': ['bar', 'baz'],
        'food': {
            'fruit': ['banana', 'kiwi', 'apple'],
            'vegetables': ['carrot', 'peas', 'broccoli']
        }
    }
    return jsonify(sample_data)


@mod.route('/blueprint/test4', methods=['POST'])
def test4():
    """ Example of using wtforms to validate user input on a POST request """
    form = ExampleForm()
    if form.validate_on_submit():  # if this is true, all the form validators were met
        integer = form.integer.data
        string = form.string.data
        password = form.password.data
        hidden = form.hidden.data
        ip_addr = form.ip_address.data
        positive_even_int = form.positive_even_int.data
        # Do something with data passed in from the form
    else:
        # Form validation failed, pass back errors to the caller (angular.js in this case)
        # and let them display those errors to the user
        return jsonify(form.errors.items())


@mod.route('/blueprint/test5', methods=['GET'])
def test5():
    """ Return a list of all usernames currently in the database (will be empty for now) """
    users = ExampleUser.query.all()
    return jsonify({'database_users': users})
