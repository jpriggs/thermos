from thermos import db
from datetime import datetime
from sqlalchemy import desc
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

# Creates a many to many relationship in the database (not accessed by the user)
tags = db.Table('bookmark_tag',
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
	db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmark.id'))
)

# Sets up the Bookmark database table
class Bookmark(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.Text, nullable=False)
	date = db.Column(db.DateTime, default=datetime.utcnow)
	description = db.Column(db.String(300))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	_tags = db.relationship('Tag', secondary=tags, lazy='joined',
							backref=db.backref('bookmarks', lazy='dynamic'))

	# Displays the most recently added bookmarks
	@staticmethod
	def newest(num):
		return Bookmark.query.order_by(desc(Bookmark.date)).limit(num)

	@property
	def tags(self):
		return ",".join([t.name for t in self._tags])

	@tags.setter
	def tags(self, string):
		if string:
			self._tags = [Tag.getOrCreate(name) for name in string.split(',')]
		else:
			self._tags = []

	def __repr__(self):
		return "<Bookmark '{}': '{}'>".format(self.description, self.url)

# Sets up the User database table
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)
	bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')
	password_hash = db.Column(db.String)

	# Creates a property in the database that is write only and can't be
	# accessed by the user, only the app
	@property
	def password(self):
		raise AttributeError('password: write-only field')

	# Creates the password hash and saves it to the passwordHash variable
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	# Hashes the users current login password and compares it against the
	# hash in the database
	def checkPassword(self, password):
		return check_password_hash(self.password_hash, password)

	@staticmethod
	def getByUsername(username):
		return User.query.filter_by(username=username).first()

	@staticmethod
	def getByEmail(email):
		return User.query.filter_by(email=email).first()

	def __repr__(self):
		return "<User '{}'>".format(self.username)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(25), nullable=False, unique=True, index=True)

	@staticmethod
	def getOrCreate(name):
		try:
			return Tag.query.filter_by(name=name).one()
		except:
			return Tag(name=name)

	@staticmethod
	def all():
		return Tag.query.all()

	def __repr__(self):
		return self.name
