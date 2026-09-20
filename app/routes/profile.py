from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import User


profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile_with_cars")
def profile_with_cars():
    return render_template("profile_with_cars.html")


@profile_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def api_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Користувача не знайдено"}), 404

    return jsonify({
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "cars": [
            {
                "id": car.id,
                "name": car.name,
                "engine": car.engine,
                "fuel_consumption": car.fuel_consumption,
                "register": car.register
            } for car in user.cars
        ]
    })
