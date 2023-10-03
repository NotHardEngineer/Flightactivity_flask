from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from src.parsing import save_tolmachovo_tables, parse_saved_tolmachovo_html
from src.models import *

bp_main = Blueprint('main', __name__)


@bp_main.route("/", methods=("GET", "POST"))
def main():
    return render_template("index.html")


@bp_main.route("/test")
def test_write():
    save_tolmachovo_tables()
    parse_saved_tolmachovo_html()
    return render_template("index.html")
