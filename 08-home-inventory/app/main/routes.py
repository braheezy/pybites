from app.main import bp
from flask import render_template


@bp.route('/')
def hello_world():
    return render_template("index.html")