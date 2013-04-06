from wtforms import TextField, PasswordField, RadioField, BooleanField, SubmitField, validators
from flask.ext.wtf import Form

# TODO: Complete forms etc.

class Signup(Form):
    username = TextField("Username:", [validators.Length(min=6, message="Too short. At least 6 characters."),
                                       validators.Required(message="A username is required.")])
    password = PasswordField("Password:", [validators.Length(min=6, message="Come on... 6 characters at the least."),
                                           validators.Required(message="A password is, obviously, required.")])
    repeat_password = PasswordField("Repeat Password:", [validators.EqualTo('password',
                                                         message='Passwords must match.')])
    email = TextField("Email:", [validators.Email(message="That is not a valid email."),
                                 validators.Required(message="Required - don't even try.")])
    first_name = TextField("First Name:")
    last_name = TextField("Last Name:")
    gender = RadioField("Gender:", [validators.InputRequired(message="Please pick one.")],
                        choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')


class Login(Form):
    username = TextField("Username", [validators.Length(min=6, message="At least 6 characters."),
                                      validators.Required(message="A username is required.")])
    password = PasswordField("Password", [validators.Length(min=6, message="6 characters at the least."),
                                          validators.Required(message="A password is, obviously, required.")])
    remember = BooleanField("Remember?", default=False)
