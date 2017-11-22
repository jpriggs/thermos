from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user

from . import auth
from .. import db
from ..models import User
from thermos.forms import LoginForm, SignupForm

@auth.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		# Login and validate the user
		user = User.getByUsername(form.username.data)
		if user is not None and user.checkPassword(form.password.data):
			login_user(user, form.rememberMe.data)
			flash("Logged in sucessfully as {}.".format(user.username))
			return redirect(request.args.get('next') or url_for('bookmarks.user',
													username=user.username))
		flash('Incorrect username or password')
	return render_template("login.html", form=form)

@auth.route("/logout", methods=["GET", "POST"])
def logout():
	logout_user()
	return redirect(url_for('main.index'))

@auth.route("/signup", methods=["GET", "POST"])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,
					username=form.username.data,
					password=form.password.data)
		invalidUsername = User.getByUsername(form.username.data)
		invalidEmail = User.getByEmail(form.email.data)
		if invalidUsername is None and invalidEmail is None:
			db.session.add(user)
			db.session.commit()
			flash('Welcome, {}! Please login.'.format(user.username))
			return redirect(url_for('login'))
		elif invalidUsername:
			flash('Username has already been registered by another user.')
		elif invalidEmail:
			flash('E-mail address has already been registered by another user.')
	return render_template("signup.html", form=form)
