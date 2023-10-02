from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.models.models import *

bp_main = Blueprint('main', __name__)

@bp_main.route("/", methods=("GET", "POST"))
def main():
    return render_template("index.html")
