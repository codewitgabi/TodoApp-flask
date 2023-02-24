from flask import Blueprint

bp = Blueprint("todo", __name__)
auth = Blueprint("auth", __name__, url_prefix="/auth")