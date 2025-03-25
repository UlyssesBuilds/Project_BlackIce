# flask_app/api/trade.py
from flask import Blueprint, request, jsonify
from flask_app.models import db, Trade, Market
from flask_jwt_extended import jwt_required, get_jwt_identity

trade_bp = Blueprint('trade', __name__)

@trade_bp.route('/trade', methods=['POST'])
@jwt_required()
def place_trade():
    data = request.json
    user_id = get_jwt_identity()

    required_fields = ["market_id", "outcome", "amount"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    market = Market.query.get(data["market_id"])
    if not market:
        return jsonify({"error": "Market not found"}), 404

    if market.is_resolved:
        return jsonify({"error": "Market is already resolved"}), 400

    if data["outcome"] not in ["yes", "no"]:
        return jsonify({"error": "Invalid outcome, choose 'yes' or 'no'"}), 400

    price = market.outcome_yes_price if data["outcome"] == "yes" else market.outcome_no_price
    new_trade = Trade(
        user_id=user_id,
        market_id=data["market_id"],
        outcome=data["outcome"],
        amount=data["amount"],
        price=price
    )

    db.session.add(new_trade)
    db.session.commit()

    return jsonify(new_trade.to_dict()), 201
