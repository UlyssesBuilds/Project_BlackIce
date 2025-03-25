# flask_app/api/market.py
from flask import Blueprint, request, jsonify
from flask_app.models import db, Market
from flask_jwt_extended import jwt_required, get_jwt_identity

market_bp = Blueprint('market', __name__)

# 🟢 POST: Create a new prediction market
@market_bp.route('/markets', methods=['POST'])
@jwt_required()
def create_market():
    data = request.json
    user_id = get_jwt_identity()

    required_fields = ["name", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Market name and description are required"}), 400

    new_market = Market(
        name=data["name"],
        description=data["description"],
        created_by=user_id,
        outcome_yes_price=data.get("outcome_yes_price", 0.5),  # Default to 50-50 probability
        outcome_no_price=data.get("outcome_no_price", 0.5)
    )

    db.session.add(new_market)
    db.session.commit()

    return jsonify(new_market.to_dict()), 201

# 🟢 GET: Fetch all markets (open & closed)
@market_bp.route('/markets', methods=['GET'])
def get_markets():
    show_resolved = request.args.get("resolved", "false").lower() == "true"
    
    markets = Market.query.filter_by(is_resolved=show_resolved).all()
    return jsonify([market.to_dict() for market in markets]), 200