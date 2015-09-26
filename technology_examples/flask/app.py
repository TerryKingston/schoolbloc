from flask import Flask, url_for, redirect, render_template
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import required

# Main flask routing/etc object
app = Flask(__name__)

# Secret key used to provide csrf protection on form posts
app.secret_key = 'SuperSecretKey'


# Simple routing examples
@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/test')
def testing():
    return "This is a test"


# Example of creating a redirect, and dynamically getting the url of a flask endpoint
@app.route('/redirect')
def redirect_test():
    return redirect(url_for('testing'))


# Server side templating. Probably wont be used much because of angular.js
@app.route('/template')
def template_test():
    team_members = ['Landon', 'Terry', 'Ben', 'Ryan']
    return render_template('template.html', names=team_members)


# Data encoded directly in url (not standard GET style)
@app.route('/data/<anything>')
def data_in_url(anything):
    return "You passed '{}' in the url!".format(anything)


# Allowing posts, and using wtforms (form library, built in csrf support, etc)
class TestForm(Form):
    username = StringField('Username', validators=[required()])
    notes = TextAreaField('Notes', validators=[required()])


@app.route('/forms', methods=['GET', 'POST'])
def post_example():
    form = TestForm()

    # This checks if the request type is a post and if the validators for this
    # form are all met
    if form.validate_on_submit():
        username = form.username.data
        notes = form.notes.data
        return "POST REQUEST: {} - {}".format(username, notes)
    return render_template("form.html", form=form)


# Exceptions debugging in flask, can examine variables, stack, etc.
@app.route('/exception')
def exception():
    a = 0
    b = 1
    return "1 / 0 = {}".format(b / a)


# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True, port=5000)
