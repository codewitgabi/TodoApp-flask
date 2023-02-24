from .blueprint import bp, auth
from flask import request, session, render_template, url_for, redirect, escape, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db
import functools


@bp.before_app_request
@auth.before_app_request
def load_logged_in_user():
	user_id = session.get("user_id")
	
	if user_id is not None:
		g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
	else:
		g.user = None


def login_required(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		if g.user is None:
			return redirect(url_for("auth.login"))
		return func(*args, **kwargs)
	return wrapper
	

def already_logged_in(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		if g.user is not None:
			return redirect(url_for("todo.view_tasks"))
		return func(*args, **kwargs)
	return wrapper
	

# Authentication Views
@auth.route("/signup/", methods=["GET", "POST"])
@already_logged_in
def signup():
	error = None
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		
		db = get_db()
		user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
		
		if user:
			error = "User with username already exists"
		else:
			db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
			db.commit()
			return redirect(url_for("auth.login"))
			
		flash(error)
		
	return render_template("auth/signup.html")
	

@auth.route("/signin/", methods=["GET", "POST"])
@already_logged_in
def login():
	error = None
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		
		db = get_db()
		user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
		
		if user is not None:
			if not check_password_hash(user["password"], password):
				error = "Incorrect username or password"
		
			if error is None:
				session.clear()
				session["user_id"] = user["id"]
				return redirect(url_for("todo.view_tasks"))
		else:
			error = "Incorrect username or password"
			
		flash(error)
		
	return render_template("auth/signin.html")


@auth.route("/logout/", methods=["GET"])
def logout():
	session.clear()
	return redirect(url_for("auth.login"))


# Task Manager Views

@bp.route("/", methods= ["GET", "POST"])
@login_required
def view_tasks():
	# get search query
	q = request.args.get("q", "")
	# query data
	db = get_db()
	tasks = db.execute("SELECT * FROM task WHERE author_id = ? ORDER BY due_date", (g.user["id"],)).fetchall()
	
	return render_template("task/tasks.html", tasks= tasks)
	

@bp.route("/create/", methods=["GET", "POST"])
@login_required
def create_task():
	if request.method == "POST":
		title = request.form.get("title")
		content = request.form.get("content")
		due_date = request.form.get("due_date")
		
		db = get_db()
		db.execute("INSERT INTO task (title, author_id, content, due_date) VALUES (?, ?, ?, ?)", (title, g.user["id"], content, due_date))
		db.commit()
		
		return redirect(url_for("todo.view_tasks"))
		
	return render_template("task/create.html")


@bp.route("/delete/<int:id>/", methods=["GET"])
@login_required
def delete_task(id):
	db = get_db()
	db.execute("DELETE FROM task WHERE id = ? AND author_id = ?", (escape(id), g.user["id"]))
	db.commit()
	
	return redirect(url_for("todo.view_tasks"))


@bp.route("/update/<int:id>/", methods=["GET", "POST"])
@login_required
def update_task(id):
	db = get_db()
	post = db.execute("SELECT * FROM task WHERE id = ? AND author_id = ?", (escape(id), g.user["id"])).fetchone()
	
	if request.method == "POST":
		title = request.form.get("title")
		content = request.form.get("content")
		due_date = request.form.get("due_date")
		
		#update database
		db.execute("UPDATE task SET title = ?, content = ?, due_date = ? WHERE id = ?", (title, content, due_date, id))
		db.commit()
		return redirect(url_for("todo.view_tasks"))
	
	return render_template("task/update.html", title=post["title"], content=post["content"], due_date=post["due_date"])

