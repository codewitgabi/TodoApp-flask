from .blueprint import bp
from flask import request, session, render_template, url_for, redirect, escape
from .db import get_db


@bp.route("/", methods= ["GET", "POST"])
def view_tasks():
	# get search query
	q = request.args.get("q", "")
	# query data
	db = get_db()
	tasks = db.execute("SELECT * FROM task ORDER BY due_date").fetchall()
	
	return render_template("tasks.html", tasks= tasks)
	

@bp.route("/create/", methods=["GET", "POST"])
def create_task():
	if request.method == "POST":
		title = request.form.get("title")
		content = request.form.get("content")
		due_date = request.form.get("due_date")
		
		db = get_db()
		db.execute("INSERT INTO task (title, content, due_date) VALUES (?, ?, ?)", (title, content, due_date))
		db.commit()
		
		return redirect(url_for("todo.view_tasks"))
		
	return render_template("create.html")


@bp.route("/delete/<int:id>/", methods=["GET"])
def delete_task(id):
	db = get_db()
	db.execute("DELETE FROM task WHERE id = ?", (escape(id),))
	db.commit()
	
	return redirect(url_for("todo.view_tasks"))


@bp.route("/update/<int:id>/", methods=["GET", "POST"])
def update_task(id):
	db = get_db()
	post = db.execute("SELECT * FROM task WHERE id = ?", (escape(id),)).fetchone()
	
	if request.method == "POST":
		title = request.form.get("title")
		content = request.form.get("content")
		due_date = request.form.get("due_date")
		
		#update database
		db.execute("UPDATE task SET title = ?, content = ?, due_date = ? WHERE id = ?", (title, content, due_date, id))
		db.commit()
		return redirect(url_for("todo.view_tasks"))
	
	return render_template("update.html", title=post["title"], content=post["content"], due_date=post["due_date"])