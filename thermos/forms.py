from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField
from flask.ext.wtf.html5 import URLField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, url, ValidationError

from thermos.models import User

class BookmarkForm(Form):
	url = URLField('The URL for your bookmark:', validators=[DataRequired(), url()])
	description = StringField('Add an optional description:')
	tags = StringField('Tags', validators=[Regexp(r'^[a-zA-Z0-9, ]*$',
					message="Tags can only contain letters and numbers")])

	def validate(self):
		if not self.url.data.startswith("http://") or\
			self.url.data.startswith("https://"):
			self.url.data = "http://" + self.url.data

		if not Form.validate(self):
			return False

		if not self.description.data:
			self.description.data = self.url.data

		# Filter out empty and duplicate tag names
		stripped = [t.strip() for t in self.tags.data.split(',')]
		notEmpty = [tag for tag in stripped if tag]
		tagset = set(notEmpty)
		self.tags.data = ",".join(tagset)

		return True

class LoginForm(Form):
	username = StringField('Your Username:', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	rememberMe = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

class SignupForm(Form):
	username = StringField('Username',
					validators=[
						DataRequired(), Length(3, 80),
						Regexp('^[A-Za-z0-9_]{3,}$',
							message='Usernames consist of numbers, letters,'
									'and underscores.')])
	password = PasswordField('Password',
					validators=[
						DataRequired(),
						EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confirm password', validators=[DataRequired()])
	email = StringField('Email',
						validators=[DataRequired(), Length(1, 120), Email()])

	def validateEmail(self, email_field):
		if User.query.filter_by(email=email_field.data).first():
			raise ValidationError('There already is a user with this email address.')

	def validateUsername(self, username_field):
		if User.query.filter_by(username=username_field.data).first():
			raise ValidationError('This username is already taken.')
