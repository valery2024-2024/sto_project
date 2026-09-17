from flask import Blueprint, render_template


profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile_with_cars")
def profile_with_cars():
    return render_template("profile_with_cars.html")
