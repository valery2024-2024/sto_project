from flask import Blueprint, jsonify, render_template, request
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

    try:
        new_car = Car(
            name=data['name'],
            engine=int(data['engine']),
            fuel_consumption=float(data['fuel_consumption']),
            register=data.get('register', False),
            user_id=user_id
        )
        db.session.add(new_car)
        db.session.commit()
        return jsonify({"msg": "РђРІС‚РѕРјРѕР±С–Р»СЊ РґРѕРґР°РЅРѕ СѓСЃРїС–С€РЅРѕ!"}), 201
    except Exception as e:
        return jsonify({"msg": f"РџРѕРјРёР»РєР°: {str(e)}"}), 400


@cars_bp.route("/add_car", methods=["GET"])
def add_car():
    return render_template('add_car.html')
