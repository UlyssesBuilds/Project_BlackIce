# flask_app/api/market.py
from flask import Blueprint, request, jsonify
from flask_app.models import db, Market
from flask_jwt_extended import jwt_required, get_jwt_identity

market_bp = Blueprint('market', __name__)

@market_bp.route('/markets', methods=['POST'])
@jwt_required()
def create_market():
    data = request.json
    user_id = get_jwt_identity()

    if "name" not in data:
        return jsonify({"error": "Market name is required"}), 400

    new_market = Market(
        name=data["name"],
        description=data.get("description", ""),
        created_by=user_id
    )

    db.session.add(new_market)
    db.session.commit()

    return jsonify(new_market.to_dict()), 201


@market_bp.route('/markets', methods=['GET'])
def get_markets():
    markets = Market.query.filter_by(is_resolved=False).all()  # Only show unresolved markets
    return jsonify([market.to_dict() for market in markets]), 200
