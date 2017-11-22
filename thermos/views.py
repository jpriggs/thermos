import json

from flask import Flask, render_template, url_for, request, redirect, flash, abort
from flask_login import login_required, login_user, logout_user, current_user

from thermos import app, db, login_manager
from thermos.forms import BookmarkForm, LoginForm, SignupForm
from thermos.models import User, Bookmark, Tag

# Fetch user id from the database if it exists
@login_manager.user_loader
def loadUser(userid):
	return User.query.get(int(userid))

# view functions
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', newBookmarks=Bookmark.newest(5))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
	form = BookmarkForm()
	# Checks the http request method and the user submitted data in the form
	if form.validate_on_submit():
		url = form.url.data
		description = form.description.data
		tags = form.tags.data
		bm = Bookmark(user=current_user, url=url, description=description, tags=tags)
		db.session.add(bm)
		db.session.commit()
		flash("Stored '{}'".format(description))
		return redirect(url_for('index'))
	return render_template('add.html', form=form)

@app.route('/edit/<int:bookmark_id>', methods=["GET", "POST"])
@login_required
def editBookmark(bookmark_id):
	bookmark = Bookmark.query.get_or_404(bookmark_id)
	if current_user != bookmark.user:
		abort(403)
	form  = BookmarkForm(obj=bookmark)
	if form.validate_on_submit():
		form.populate_obj(bookmark)
		db.session.commit()
		flash("Stored '{}'".format(bookmark.description))
		return redirect(url_for('user', username=current_user.username))
	return render_template('bookmark_form.html', form=form, title="Edit bookmark")

@app.route('/delete/<int:bookmark_id>', methods=["GET", "POST"])
def deleteBookmark(bookmark_id):
	bookmark = Bookmark.query.get_or_404(bookmark_id)
	if current_user != bookmark.user:
		abort(403)
	if request.method == "POST":
		db.session.delete(bookmark)
		db.session.commit()
		flash("Deleted '{}'".format(bookmark.description))
		return redirect(url_for('user', username=current_user.username))
	else:
		flash("Please confirm deleting the bookmark.")
	return render_template('confirm_delete.html', bookmark=bookmark, nolinks=True)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		# Login and validate the user
		user = User.getByUsername(form.username.data)
		if user is not None and user.checkPassword(form.password.data):
			login_user(user, form.rememberMe.data)
			flash("Logged in sucessfully as {}.".format(user.username))
			return redirect(request.args.get('next') or url_for('user', username=user.username))
		flash('Incorrect username or password')
	return render_template("login.html", form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route("/signup", methods=["GET", "POST"])
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

@app.route('/tag/<name>')
def tag(name):
	tag = Tag.query.filter_by(name=name).first_or_404()
	return render_template('tag.html', tag=tag)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
	return render_template('500.html'), 500

@app.context_processor
def injectTags():
	return dict(allTags=Tag.all)
