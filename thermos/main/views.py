from flask import render_template

from . import main
from .. import login_manager
from ..models import User, Bookmark, Tag

# Fetch user id from the database if it exists
@login_manager.user_loader
def loadUser(userid):
	return User.query.get(int(userid))

# view functions
@main.route('/')
def index():
	return render_template('index.html', newBookmarks=Bookmark.newest(5))

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

@main.app_context_processor
def injectTags():
	return dict(allTags=Tag.all)
