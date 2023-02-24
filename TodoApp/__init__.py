from flask import Flask
import os


def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	
	# apps base dir
	BASE_DIR = app.instance_path
	
	app.config.from_mapping(
		SECRET_KEY="kabsh63y2gwus82ns",
		DATABASE=os.path.join(BASE_DIR, "db.sqlite")
	)
	
	if test_config is None:
		app.config.from_pyfile("config.py", silent=True)
	else:
		app.config.from_mapping(test_config)
		
	try:
		os.makedirs(BASE_DIR)
	except OSError:
		pass
	
	# imports	
	from . import db
	from .views import bp
	
	db.init_app(app)
	app.register_blueprint(bp)
	
	return app