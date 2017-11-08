import phonenumbers

from authy import AuthyFormatException
from authy.api import AuthyApiClient
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError
from phonenumbers.phonenumberutil import NumberParseException

from . import app
from .models import User


authy_api = AuthyApiClient(app.config['ACCOUNT_SECURITY_API_KEY'])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

    def validate(self):
        if not super(LoginForm, self).validate():
            return False
        self.user = User.query.get(self.username.data)
        if not self.user or not self.user.check_password(self.password.data):
            self.errors['non_field'] = 'Invalid username and/or password'
            return False
        return True


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired()])
    country_code = StringField('country_code', validators=[DataRequired()])
    phone_number = StringField('phone_number', validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.get(field.data):
            raise ValidationError('Username already taken')

    def validate_country_code(self, field):
        if not field.data.startswith('+'):
            field.data = '+' + field.data

    def validate(self):
        if not super(RegistrationForm, self).validate():
            return False
        if self.password.data != self.confirm_password.data:
            self.errors['non_field'] = 'Password and confirmation did not match'
            return False

        phone_number = self.country_code.data + self.phone_number.data
        try:
            phone_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(phone_number):
                self.phone_number.errors.append('Invalid phone number')
                return False
        except NumberParseException as e:
            self.phone_number.errors.append(str(e))
            return False
        return True


class TokenVerificationForm(FlaskForm):
    token = StringField('token', validators=[DataRequired()])

    def __init__(self, authy_id):
        self.authy_id = authy_id
        super(TokenVerificationForm, self).__init__()

    def validate_token(self, field):
        try:
            verification = authy_api.tokens.verify(self.authy_id, self.token.data)
            if not verification.ok():
                self.token.errors.append('Invalid Token')
                return False
        except AuthyFormatException as e:
            self.token.errors.append(str(e))
            return False
        return True
