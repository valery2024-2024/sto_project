from flask import Blueprint, render_template


profile_bp = Blueprint("profile", __name__)


def profile_with_cars():
    return render_template("profile_with_cars.html")


@profile_bp.record_once
def register_profile_routes(state):
    state.app.add_url_rule(
        "/profile_with_cars",
        endpoint="profile_with_cars",
        view_func=profile_with_cars,
    )
