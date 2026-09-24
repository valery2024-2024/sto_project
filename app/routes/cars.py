from flask import Blueprint, current_app, jsonify, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Car


cars_bp = Blueprint("cars", __name__)


@cars_bp.route("/api/add_car", methods=["GET", "POST"])
@jwt_required()
def api_add_car():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "Invalid or missing JSON"}), 400

    required_fields = ("name", "engine", "fuel_consumption")
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    name = data["name"]
    if not isinstance(name, str) or not name.strip():
        return jsonify({"msg": "Invalid name"}), 400
    name = name.strip()

    try:
        engine = int(data["engine"])
        fuel_consumption = float(data["fuel_consumption"])
    except (TypeError, ValueError):
        return jsonify({"msg": "Invalid numeric fields"}), 400

    new_car = Car(
        name=name,
        engine=engine,
        fuel_consumption=fuel_consumption,
        register=data.get('register', False),
        user_id=user_id
    )

    try:
        db.session.add(new_car)
        db.session.commit()
        return jsonify({"msg": "РђРІС‚РѕРјРѕР±С–Р»СЊ РґРѕРґР°РЅРѕ СѓСЃРїС–С€РЅРѕ!"}), 201
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to add car")
        return jsonify({"msg": "Failed to add car"}), 500


@cars_bp.route("/add_car", methods=["GET"])
def add_car():
    return render_template('add_car.html')
