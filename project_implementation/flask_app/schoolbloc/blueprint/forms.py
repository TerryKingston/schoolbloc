"""
This is a collection of html forms for this blueprint.

This is used to create html forms and do validation of them when they are submitted
to the backend. I'm not sure if we will actually pass these forms to the anular.js,
normally we embed this form into the html templates with jinja to pass the html
to the web browser, and I doubt that is how this will work with angular.js, but we
can still do this for very easy user input validation, as well as csrf protection
"""
from flask.ext.wtf import Form
from wtforms import HiddenField, IntegerField, StringField, PasswordField
from wtforms.validators import DataRequired, Optional, IPAddress, ValidationError


def even_positive_number(form, field):
    """
    This is an example of a custom validator that we coulc use with our forms
    bellow
    """
    i = field.data
    if i <= 0:
        raise ValidationError("Must be a positive number")
    if i % 2 != 0:
        raise ValidationError("Must be an even number")


class ExampleForm(Form):
    """
    An example form show the basics of wtforms. Even if we aren't passing this
    form directly to the angular.js (will have to look into that), we can use
    to do form validatioin on all user input very esaily
    """
    integer = IntegerField('Integer Input', validators=[DataRequired()])
    string = StringField('String Input', validators=[Optional()])
    password = PasswordField('Enter Password', validators=[DataRequired()])
    hidden = HiddenField('Hidden Data', validators=[Optional()])
    ip_address = StringField('IP Address', validators=[DataRequired(), IPAddress(ipv6=False)])
    positive_even_int = IntegerField('Positive Even Integer',
                                     validators=[DataRequired(), even_positive_number])
